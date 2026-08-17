<?php

namespace App\Controller;

use App\Entity\Contract;
use App\Entity\RiskFlag;
use App\Enum\ContractStatus;
use App\Repository\ContractRepository;
use App\Repository\RiskFlagRepository;
use App\Service\AuditLogger;
use App\Service\ContractStorage;
use App\Service\EngineClient;
use Symfony\Component\HttpFoundation\File\UploadedFile;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpKernel\Exception\BadRequestHttpException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\IsGranted;

#[Route('/api/contracts')]
#[IsGranted('IS_AUTHENTICATED_FULLY')]
final class ContractController extends ApiController
{
    private const DISCLAIMER = 'D4TA Shield es una segunda lectura antes de la firma, no sustituto de asesoría legal. '
        .'Este informe señala patrones de riesgo en cláusulas individuales; la decisión final es siempre humana.';

    public function __construct(
        private readonly ContractRepository $contracts,
        private readonly RiskFlagRepository $riskFlags,
        private readonly ContractStorage $storage,
        private readonly EngineClient $engine,
        private readonly AuditLogger $audit,
    ) {
    }

    #[Route('', name: 'api_contracts_list', methods: ['GET'])]
    public function list(): JsonResponse
    {
        $user = $this->getAppUser();
        $tenant = $user->getTenant();
        \assert($tenant !== null);

        $items = array_map(
            fn (Contract $c) => $this->serializeContract($c),
            $this->contracts->findByTenant($tenant),
        );

        return $this->json(['data' => $items, 'disclaimer' => self::DISCLAIMER]);
    }

    #[Route('', name: 'api_contracts_upload', methods: ['POST'])]
    public function upload(Request $request): JsonResponse
    {
        $user = $this->getAppUser();
        $tenant = $user->getTenant();
        \assert($tenant !== null);

        /** @var UploadedFile|null $file */
        $file = $request->files->get('file');
        if (!$file instanceof UploadedFile || !$file->isValid()) {
            throw new BadRequestHttpException('Multipart field "file" is required.');
        }

        $ext = strtolower($file->getClientOriginalExtension() ?: '');
        if (!\in_array($ext, ['pdf', 'docx'], true)) {
            throw new BadRequestHttpException('Only PDF and DOCX contracts are accepted.');
        }

        $contract = (new Contract())->setTenant($tenant)->setStatus(ContractStatus::Pending);
        $stored = $this->storage->store($tenant->getId(), $contract->getId(), $file);
        $contract
            ->setOriginalFilename($stored['original_filename'])
            ->setStoragePath($stored['relative_path'])
            ->setFileHash($stored['hash']);

        $this->contracts->save($contract);

        try {
            $engineResult = $this->engine->upload($stored['absolute_path'], $stored['original_filename']);
            $contract
                ->setEngineContractId((string) ($engineResult['id'] ?? ''))
                ->setClauseCount((int) ($engineResult['clause_count'] ?? 0))
                ->setStatus(ContractStatus::InReview);

            $this->contracts->save($contract);
            $this->audit->log($tenant, 'contract.upload', [
                'contract_id' => $contract->getId()->toRfc4122(),
                'engine_id' => $contract->getEngineContractId(),
                'clause_count' => $contract->getClauseCount(),
            ], $user);
        } catch (\Throwable $e) {
            $contract->setStatus(ContractStatus::Failed);
            $this->contracts->save($contract);
            $this->audit->log($tenant, 'contract.upload_failed', [
                'contract_id' => $contract->getId()->toRfc4122(),
                'error' => $e->getMessage(),
            ], $user);

            return $this->json([
                'data' => $this->serializeContract($contract),
                'error' => $e->getMessage(),
                'disclaimer' => self::DISCLAIMER,
            ], 502);
        }

        return $this->json(['data' => $this->serializeContract($contract), 'disclaimer' => self::DISCLAIMER], 201);
    }

    #[Route('/{id}/analyze', name: 'api_contracts_analyze', methods: ['POST'])]
    public function analyze(string $id): JsonResponse
    {
        $user = $this->getAppUser();
        $tenant = $user->getTenant();
        \assert($tenant !== null);

        $contract = $this->contracts->findForTenant($tenant, $id);
        if (!$contract instanceof Contract) {
            throw new NotFoundHttpException('Contract not found.');
        }
        if (!$contract->getEngineContractId()) {
            throw new BadRequestHttpException('Contract not uploaded to engine.');
        }

        try {
            $this->engine->analyze($contract->getEngineContractId());
            $report = $this->engine->report($contract->getEngineContractId());
            $this->syncRiskFlags($contract, $report);
            $contract->setStatus(ContractStatus::InReview);
            $this->contracts->save($contract);

            $this->audit->log($tenant, 'contract.analyzed', [
                'contract_id' => $contract->getId()->toRfc4122(),
                'risk_high' => $contract->getRiskHigh(),
                'discrepancies' => $contract->getDiscrepancyCount(),
            ], $user);
        } catch (\Throwable $e) {
            $contract->setStatus(ContractStatus::Failed);
            $this->contracts->save($contract);

            return $this->json(['error' => $e->getMessage(), 'disclaimer' => self::DISCLAIMER], 502);
        }

        return $this->json(['data' => $this->serializeContract($contract), 'disclaimer' => self::DISCLAIMER]);
    }

    #[Route('/{id}/report', name: 'api_contracts_report', methods: ['GET'])]
    public function report(string $id): JsonResponse
    {
        $user = $this->getAppUser();
        $tenant = $user->getTenant();
        \assert($tenant !== null);

        $contract = $this->contracts->findForTenant($tenant, $id);
        if (!$contract instanceof Contract || !$contract->getEngineContractId()) {
            throw new NotFoundHttpException('Contract not found.');
        }

        $report = $this->engine->report($contract->getEngineContractId());
        $flags = array_map(fn (RiskFlag $f) => $this->serializeFlag($f), $contract->getRiskFlags()->toArray());

        return $this->json([
            'data' => array_merge($report, [
                'contract_id' => $contract->getId()->toRfc4122(),
                'flags' => $flags,
            ]),
            'disclaimer' => self::DISCLAIMER,
        ]);
    }

    #[Route('/{id}/discrepancies', name: 'api_contracts_discrepancies', methods: ['GET'])]
    public function discrepancies(string $id): JsonResponse
    {
        $user = $this->getAppUser();
        $tenant = $user->getTenant();
        \assert($tenant !== null);

        $contract = $this->contracts->findForTenant($tenant, $id);
        if (!$contract instanceof Contract || !$contract->getEngineContractId()) {
            throw new NotFoundHttpException('Contract not found.');
        }

        $report = $this->engine->report($contract->getEngineContractId());

        return $this->json([
            'data' => $report['discrepancies'] ?? [],
            'disclaimer' => self::DISCLAIMER,
        ]);
    }

    #[Route('/{id}/flags/{flagId}/review', name: 'api_contracts_review_flag', methods: ['POST'])]
    public function reviewFlag(string $id, string $flagId): JsonResponse
    {
        $user = $this->getAppUser();
        $tenant = $user->getTenant();
        \assert($tenant !== null);

        $contract = $this->contracts->findForTenant($tenant, $id);
        if (!$contract instanceof Contract) {
            throw new NotFoundHttpException('Contract not found.');
        }

        $flag = null;
        foreach ($contract->getRiskFlags() as $f) {
            if ($f->getId()->toRfc4122() === $flagId) {
                $flag = $f;
                break;
            }
        }
        if (!$flag instanceof RiskFlag) {
            throw new NotFoundHttpException('Risk flag not found.');
        }

        $flag
            ->setHumanReviewed(true)
            ->setHumanReviewedAt(new \DateTimeImmutable())
            ->setHumanReviewedBy($user);
        $this->riskFlags->save($flag);

        $this->audit->log($tenant, 'clause.human_reviewed', [
            'contract_id' => $contract->getId()->toRfc4122(),
            'flag_id' => $flag->getId()->toRfc4122(),
            'engine_clause_id' => $flag->getEngineClauseId(),
            'risk_level' => $flag->getRiskLevel(),
            'reviewed_by' => $user->getEmail(),
            'reviewed_at' => $flag->getHumanReviewedAt()?->format(\DateTimeInterface::ATOM),
        ], $user);

        $allReviewed = true;
        foreach ($contract->getRiskFlags() as $f) {
            if ($f->getRiskLevel() === 'alto' && !$f->isHumanReviewed()) {
                $allReviewed = false;
                break;
            }
        }
        if ($allReviewed) {
            $contract->setStatus(ContractStatus::Resolved);
            $this->contracts->save($contract);
        }

        return $this->json([
            'data' => $this->serializeFlag($flag),
            'disclaimer' => self::DISCLAIMER,
        ]);
    }

    /** @param array<string, mixed> $report */
    private function syncRiskFlags(Contract $contract, array $report): void
    {
        $contract->getRiskFlags()->clear();

        $high = $medium = $low = $discrepancies = 0;
        /** @var list<array<string, mixed>> $analyses */
        $analyses = $report['analyses'] ?? [];

        foreach ($analyses as $analysis) {
            $level = (string) ($analysis['risk_level'] ?? 'bajo');
            match ($level) {
                'alto' => ++$high,
                'medio' => ++$medium,
                default => ++$low,
            };
            if (!empty($analysis['requires_priority_review'])) {
                ++$discrepancies;
            }

            $flag = (new RiskFlag())
                ->setEngineClauseId((string) ($analysis['clause_id'] ?? ''))
                ->setCategory((string) ($analysis['category'] ?? ''))
                ->setRiskLevel($level)
                ->setExplanation((string) ($analysis['explanation'] ?? ''))
                ->setQuotedEvidence((string) ($analysis['quoted_evidence'] ?? ''))
                ->setDetectedBy((string) ($analysis['detected_by'] ?? ''))
                ->setRequiresPriorityReview((bool) ($analysis['requires_priority_review'] ?? false))
                ->setDiscrepancyReason($analysis['discrepancy_reason'] ?? null);
            $contract->addRiskFlag($flag);
        }

        $contract
            ->setRiskHigh($high)
            ->setRiskMedium($medium)
            ->setRiskLow($low)
            ->setDiscrepancyCount($discrepancies)
            ->setClauseCount(\count($report['clauses'] ?? []));
    }

    /** @return array<string, mixed> */
    private function serializeContract(Contract $contract): array
    {
        return [
            'id' => $contract->getId()->toRfc4122(),
            'filename' => $contract->getOriginalFilename(),
            'status' => $contract->getStatus()->value,
            'version' => $contract->getVersion(),
            'clause_count' => $contract->getClauseCount(),
            'risk_counts' => [
                'alto' => $contract->getRiskHigh(),
                'medio' => $contract->getRiskMedium(),
                'bajo' => $contract->getRiskLow(),
            ],
            'discrepancy_count' => $contract->getDiscrepancyCount(),
            'created_at' => $contract->getCreatedAt()->format(\DateTimeInterface::ATOM),
            'updated_at' => $contract->getUpdatedAt()->format(\DateTimeInterface::ATOM),
        ];
    }

    /** @return array<string, mixed> */
    private function serializeFlag(RiskFlag $flag): array
    {
        return [
            'id' => $flag->getId()->toRfc4122(),
            'engine_clause_id' => $flag->getEngineClauseId(),
            'category' => $flag->getCategory(),
            'risk_level' => $flag->getRiskLevel(),
            'explanation' => $flag->getExplanation(),
            'quoted_evidence' => $flag->getQuotedEvidence(),
            'detected_by' => $flag->getDetectedBy(),
            'requires_priority_review' => $flag->requiresPriorityReview(),
            'discrepancy_reason' => $flag->getDiscrepancyReason(),
            'human_reviewed' => $flag->isHumanReviewed(),
            'human_reviewed_at' => $flag->getHumanReviewedAt()?->format(\DateTimeInterface::ATOM),
        ];
    }
}

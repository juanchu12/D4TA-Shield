<?php

namespace App\Entity;

use App\Repository\RiskFlagRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Uid\Uuid;

#[ORM\Entity(repositoryClass: RiskFlagRepository::class)]
#[ORM\Table(name: 'risk_flags')]
class RiskFlag
{
    #[ORM\Id]
    #[ORM\Column(type: 'uuid', unique: true)]
    private Uuid $id;

    #[ORM\ManyToOne(inversedBy: 'riskFlags')]
    #[ORM\JoinColumn(nullable: false, onDelete: 'CASCADE')]
    private ?Contract $contract = null;

    #[ORM\Column(length: 64)]
    private string $engineClauseId = '';

    #[ORM\Column(length: 64)]
    private string $category = '';

    #[ORM\Column(length: 16)]
    private string $riskLevel = '';

    #[ORM\Column(type: Types::TEXT)]
    private string $explanation = '';

    #[ORM\Column(type: Types::TEXT)]
    private string $quotedEvidence = '';

    #[ORM\Column(length: 16)]
    private string $detectedBy = '';

    #[ORM\Column]
    private bool $requiresPriorityReview = false;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $discrepancyReason = null;

    #[ORM\Column]
    private bool $humanReviewed = false;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE, nullable: true)]
    private ?\DateTimeImmutable $humanReviewedAt = null;

    #[ORM\ManyToOne]
    #[ORM\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?User $humanReviewedBy = null;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private \DateTimeImmutable $createdAt;

    public function __construct()
    {
        $this->id = Uuid::v7();
        $this->createdAt = new \DateTimeImmutable();
    }

    public function getId(): Uuid
    {
        return $this->id;
    }

    public function getContract(): ?Contract
    {
        return $this->contract;
    }

    public function setContract(?Contract $contract): static
    {
        $this->contract = $contract;

        return $this;
    }

    public function getEngineClauseId(): string
    {
        return $this->engineClauseId;
    }

    public function setEngineClauseId(string $engineClauseId): static
    {
        $this->engineClauseId = $engineClauseId;

        return $this;
    }

    public function getCategory(): string
    {
        return $this->category;
    }

    public function setCategory(string $category): static
    {
        $this->category = $category;

        return $this;
    }

    public function getRiskLevel(): string
    {
        return $this->riskLevel;
    }

    public function setRiskLevel(string $riskLevel): static
    {
        $this->riskLevel = $riskLevel;

        return $this;
    }

    public function getExplanation(): string
    {
        return $this->explanation;
    }

    public function setExplanation(string $explanation): static
    {
        $this->explanation = $explanation;

        return $this;
    }

    public function getQuotedEvidence(): string
    {
        return $this->quotedEvidence;
    }

    public function setQuotedEvidence(string $quotedEvidence): static
    {
        $this->quotedEvidence = $quotedEvidence;

        return $this;
    }

    public function getDetectedBy(): string
    {
        return $this->detectedBy;
    }

    public function setDetectedBy(string $detectedBy): static
    {
        $this->detectedBy = $detectedBy;

        return $this;
    }

    public function requiresPriorityReview(): bool
    {
        return $this->requiresPriorityReview;
    }

    public function setRequiresPriorityReview(bool $requiresPriorityReview): static
    {
        $this->requiresPriorityReview = $requiresPriorityReview;

        return $this;
    }

    public function getDiscrepancyReason(): ?string
    {
        return $this->discrepancyReason;
    }

    public function setDiscrepancyReason(?string $discrepancyReason): static
    {
        $this->discrepancyReason = $discrepancyReason;

        return $this;
    }

    public function isHumanReviewed(): bool
    {
        return $this->humanReviewed;
    }

    public function setHumanReviewed(bool $humanReviewed): static
    {
        $this->humanReviewed = $humanReviewed;

        return $this;
    }

    public function getHumanReviewedAt(): ?\DateTimeImmutable
    {
        return $this->humanReviewedAt;
    }

    public function setHumanReviewedAt(?\DateTimeImmutable $humanReviewedAt): static
    {
        $this->humanReviewedAt = $humanReviewedAt;

        return $this;
    }

    public function getHumanReviewedBy(): ?User
    {
        return $this->humanReviewedBy;
    }

    public function setHumanReviewedBy(?User $humanReviewedBy): static
    {
        $this->humanReviewedBy = $humanReviewedBy;

        return $this;
    }

    public function getCreatedAt(): \DateTimeImmutable
    {
        return $this->createdAt;
    }
}

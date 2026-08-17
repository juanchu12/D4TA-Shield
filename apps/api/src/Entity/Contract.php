<?php

namespace App\Entity;

use App\Enum\ContractStatus;
use App\Repository\ContractRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Uid\Uuid;
use Symfony\Component\Validator\Constraints as Assert;

#[ORM\Entity(repositoryClass: ContractRepository::class)]
#[ORM\Table(name: 'contracts')]
#[ORM\HasLifecycleCallbacks]
class Contract
{
    #[ORM\Id]
    #[ORM\Column(type: 'uuid', unique: true)]
    private Uuid $id;

    #[ORM\ManyToOne(inversedBy: 'contracts')]
    #[ORM\JoinColumn(nullable: false)]
    private ?Tenant $tenant = null;

    #[ORM\Column(length: 255)]
    #[Assert\NotBlank]
    private string $originalFilename = '';

    #[ORM\Column(length: 512)]
    private string $storagePath = '';

    #[ORM\Column(length: 64)]
    private string $fileHash = '';

    #[ORM\Column(length: 64, nullable: true)]
    private ?string $engineContractId = null;

    #[ORM\Column(length: 32, enumType: ContractStatus::class)]
    private ContractStatus $status = ContractStatus::Pending;

    #[ORM\Column]
    private int $version = 1;

    #[ORM\Column]
    private int $clauseCount = 0;

    #[ORM\Column]
    private int $riskHigh = 0;

    #[ORM\Column]
    private int $riskMedium = 0;

    #[ORM\Column]
    private int $riskLow = 0;

    #[ORM\Column]
    private int $discrepancyCount = 0;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private \DateTimeImmutable $createdAt;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private \DateTimeImmutable $updatedAt;

    /** @var Collection<int, RiskFlag> */
    #[ORM\OneToMany(mappedBy: 'contract', targetEntity: RiskFlag::class, cascade: ['persist', 'remove'], orphanRemoval: true)]
    private Collection $riskFlags;

    public function __construct()
    {
        $this->id = Uuid::v7();
        $now = new \DateTimeImmutable();
        $this->createdAt = $now;
        $this->updatedAt = $now;
        $this->riskFlags = new ArrayCollection();
    }

    #[ORM\PreUpdate]
    public function onPreUpdate(): void
    {
        $this->updatedAt = new \DateTimeImmutable();
    }

    public function getId(): Uuid
    {
        return $this->id;
    }

    public function getTenant(): ?Tenant
    {
        return $this->tenant;
    }

    public function setTenant(?Tenant $tenant): static
    {
        $this->tenant = $tenant;

        return $this;
    }

    public function getOriginalFilename(): string
    {
        return $this->originalFilename;
    }

    public function setOriginalFilename(string $originalFilename): static
    {
        $this->originalFilename = $originalFilename;

        return $this;
    }

    public function getStoragePath(): string
    {
        return $this->storagePath;
    }

    public function setStoragePath(string $storagePath): static
    {
        $this->storagePath = $storagePath;

        return $this;
    }

    public function getFileHash(): string
    {
        return $this->fileHash;
    }

    public function setFileHash(string $fileHash): static
    {
        $this->fileHash = $fileHash;

        return $this;
    }

    public function getEngineContractId(): ?string
    {
        return $this->engineContractId;
    }

    public function setEngineContractId(?string $engineContractId): static
    {
        $this->engineContractId = $engineContractId;

        return $this;
    }

    public function getStatus(): ContractStatus
    {
        return $this->status;
    }

    public function setStatus(ContractStatus $status): static
    {
        $this->status = $status;

        return $this;
    }

    public function getVersion(): int
    {
        return $this->version;
    }

    public function setVersion(int $version): static
    {
        $this->version = $version;

        return $this;
    }

    public function getClauseCount(): int
    {
        return $this->clauseCount;
    }

    public function setClauseCount(int $clauseCount): static
    {
        $this->clauseCount = $clauseCount;

        return $this;
    }

    public function getRiskHigh(): int
    {
        return $this->riskHigh;
    }

    public function setRiskHigh(int $riskHigh): static
    {
        $this->riskHigh = $riskHigh;

        return $this;
    }

    public function getRiskMedium(): int
    {
        return $this->riskMedium;
    }

    public function setRiskMedium(int $riskMedium): static
    {
        $this->riskMedium = $riskMedium;

        return $this;
    }

    public function getRiskLow(): int
    {
        return $this->riskLow;
    }

    public function setRiskLow(int $riskLow): static
    {
        $this->riskLow = $riskLow;

        return $this;
    }

    public function getDiscrepancyCount(): int
    {
        return $this->discrepancyCount;
    }

    public function setDiscrepancyCount(int $discrepancyCount): static
    {
        $this->discrepancyCount = $discrepancyCount;

        return $this;
    }

    public function getCreatedAt(): \DateTimeImmutable
    {
        return $this->createdAt;
    }

    public function getUpdatedAt(): \DateTimeImmutable
    {
        return $this->updatedAt;
    }

    /** @return Collection<int, RiskFlag> */
    public function getRiskFlags(): Collection
    {
        return $this->riskFlags;
    }

    public function addRiskFlag(RiskFlag $flag): static
    {
        if (!$this->riskFlags->contains($flag)) {
            $this->riskFlags->add($flag);
            $flag->setContract($this);
        }

        return $this;
    }
}

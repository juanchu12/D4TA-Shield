<?php

namespace App\Repository;

use App\Entity\Contract;
use App\Entity\Tenant;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/** @extends ServiceEntityRepository<Contract> */
class ContractRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Contract::class);
    }

    public function save(Contract $contract): void
    {
        $this->getEntityManager()->persist($contract);
        $this->getEntityManager()->flush();
    }

    /** @return list<Contract> */
    public function findByTenant(Tenant $tenant): array
    {
        return $this->findBy(['tenant' => $tenant], ['createdAt' => 'DESC']);
    }

    public function findForTenant(Tenant $tenant, string $id): ?Contract
    {
        return $this->findOneBy(['tenant' => $tenant, 'id' => $id]);
    }
}

<?php

namespace App\Repository;

use App\Entity\RiskFlag;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/** @extends ServiceEntityRepository<RiskFlag> */
class RiskFlagRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, RiskFlag::class);
    }

    public function save(RiskFlag $flag): void
    {
        $this->getEntityManager()->persist($flag);
        $this->getEntityManager()->flush();
    }
}

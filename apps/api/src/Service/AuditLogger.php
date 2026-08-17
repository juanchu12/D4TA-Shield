<?php

namespace App\Service;

use App\Entity\AuditLog;
use App\Entity\Tenant;
use App\Entity\User;
use App\Repository\AuditLogRepository;

final class AuditLogger
{
    public function __construct(
        private readonly AuditLogRepository $auditLogs,
    ) {
    }

    /** @param array<string, mixed> $payload */
    public function log(Tenant $tenant, string $action, array $payload = [], ?User $user = null): AuditLog
    {
        $entry = (new AuditLog())
            ->setTenant($tenant)
            ->setUser($user)
            ->setAction($action)
            ->setPayload($payload);

        $this->auditLogs->save($entry);

        return $entry;
    }
}

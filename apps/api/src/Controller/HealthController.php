<?php

namespace App\Controller;

use App\Service\EngineClient;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Attribute\Route;

final class HealthController
{
    public function __construct(private readonly EngineClient $engine)
    {
    }

    #[Route('/api/health', name: 'api_health', methods: ['GET'])]
    public function __invoke(): JsonResponse
    {
        $engine = ['ok' => false];
        try {
            $engine = array_merge(['ok' => true], $this->engine->health());
        } catch (\Throwable $e) {
            $engine = ['ok' => false, 'error' => $e->getMessage()];
        }

        return new JsonResponse([
            'status' => $engine['ok'] ? 'ok' : 'degraded',
            'service' => 'shield-api',
            'engine' => $engine,
        ]);
    }
}

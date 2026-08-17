<?php

namespace App\Service;

use Symfony\Component\Mime\Part\DataPart;
use Symfony\Component\Mime\Part\Multipart\FormDataPart;
use Symfony\Contracts\HttpClient\HttpClientInterface;
use Symfony\Contracts\HttpClient\ResponseInterface;

/** HTTP client for packages/shield-engine (FastAPI). */
final class EngineClient
{
    private HttpClientInterface $http;

    public function __construct(
        string $engineUrl,
        string $internalToken,
        HttpClientInterface $httpClient,
    ) {
        $this->http = $httpClient->withOptions([
            'base_uri' => rtrim($engineUrl, '/').'/',
            'timeout' => 180,
            'headers' => ['X-Internal-Token' => $internalToken],
        ]);
    }

    /** @return array<string, mixed> */
    public function upload(string $absolutePath, string $filename): array
    {
        $formData = new FormDataPart([
            'file' => DataPart::fromPath($absolutePath, $filename),
        ]);

        $response = $this->http->request('POST', 'contracts/upload', [
            'headers' => $formData->getPreparedHeaders()->toArray(),
            'body' => $formData->bodyToIterable(),
        ]);

        return $this->requireOk($response)->toArray(false);
    }

    /** @return array<string, mixed> */
    public function analyze(string $engineContractId): array
    {
        $response = $this->http->request('POST', 'contracts/'.$engineContractId.'/analyze');

        return $this->requireOk($response)->toArray(false);
    }

    /** @return array<string, mixed> */
    public function report(string $engineContractId): array
    {
        $response = $this->http->request('GET', 'contracts/'.$engineContractId.'/report');

        return $this->requireOk($response)->toArray(false);
    }

    /** @return array<string, mixed> */
    public function clause(string $engineContractId, string $clauseId): array
    {
        $response = $this->http->request('GET', 'contracts/'.$engineContractId.'/clause/'.$clauseId);

        return $this->requireOk($response)->toArray(false);
    }

    /** @return array<string, mixed> */
    public function health(): array
    {
        return $this->http->request('GET', 'health')->toArray(false);
    }

    private function requireOk(ResponseInterface $response): ResponseInterface
    {
        $status = $response->getStatusCode();
        if ($status >= 400) {
            throw new \RuntimeException(sprintf('Shield engine HTTP %d: %s', $status, $response->getContent(false)));
        }

        return $response;
    }
}

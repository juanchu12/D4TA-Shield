<?php

namespace App\Service;

use Symfony\Component\HttpFoundation\File\UploadedFile;
use Symfony\Component\Uid\Uuid;

final class ContractStorage
{
    public function __construct(
        private readonly string $storageDir,
    ) {
    }

    /** @return array{original_filename: string, relative_path: string, absolute_path: string, hash: string} */
    public function store(Uuid $tenantId, Uuid $contractId, UploadedFile $file): array
    {
        $tenantDir = $this->storageDir.'/'.$tenantId->toRfc4122();
        if (!is_dir($tenantDir) && !mkdir($tenantDir, 0775, true) && !is_dir($tenantDir)) {
            throw new \RuntimeException('Cannot create storage directory.');
        }

        $ext = strtolower($file->getClientOriginalExtension() ?: 'bin');
        $filename = $contractId->toRfc4122().'.'.$ext;
        $absolute = $tenantDir.'/'.$filename;
        $file->move($tenantDir, $filename);

        return [
            'original_filename' => $file->getClientOriginalName(),
            'relative_path' => $tenantId->toRfc4122().'/'.$filename,
            'absolute_path' => $absolute,
            'hash' => hash_file('sha256', $absolute) ?: '',
        ];
    }
}

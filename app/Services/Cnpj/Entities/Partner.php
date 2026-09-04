<?php

declare(strict_types = 1);

namespace App\Services\Cnpj\Entities;

readonly class Partner
{
    public function __construct(
        public string $name,
        public string $document,
    ) {
    }

    public static function createFromApi(array $data): self
    {
        return new self(
            name: $data['nome'] ?? '',
            document: $data['cpf_cnpj_socio'] ?? '',
        );
    }

    public static function createFromList(array $data): array
    {
        $partners = [];

        foreach ($data as $item) {
            $partners[] = self::createFromApi($item);
        }

        return $partners;
    }

    public static function toArray(array $partners): array
    {
        return collect($partners)
            ->map(fn (Partner $partner): array => [
                'name'     => $partner->name,
                'document' => $partner->document,
            ])
            ->toArray();
    }
}

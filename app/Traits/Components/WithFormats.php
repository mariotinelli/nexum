<?php

declare(strict_types = 1);

namespace App\Traits\Components;

trait WithFormats
{
    public function formatCnpj(string $cnpj): ?string
    {
        $unformatted = preg_replace('/[^0-9]/', '', $cnpj);

        if (strlen((string) $unformatted) !== 14) {
            return null;
        }

        return preg_replace('/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/', '$1.$2.$3/$4-$5', (string) $unformatted);
    }

    public function formatCpf(string $cpf): ?string
    {
        $unformatted = preg_replace('/[^0-9]/', '', $cpf);

        if (strlen((string) $unformatted) !== 11) {
            return null;
        }

        return preg_replace('/(\d{3})(\d{3})(\d{3})(\d{2})/', '$1.$2.$3-$4', (string) $unformatted);
    }

    public function formatPhone(string $phone): ?string
    {
        $unformatted = preg_replace('/[^0-9]/', '', $phone);

        if (strlen((string) $unformatted) < 10 || strlen((string) $unformatted) > 11) {
            return null;
        }

        if (strlen((string) $unformatted) === 10) {
            return preg_replace('/(\d{2})(\d{4})(\d{4})/', '($1) $2-$3', (string) $unformatted);
        }

        return preg_replace('/(\d{2})(\d{5})(\d{4})/', '($1) $2-$3', (string) $unformatted);
    }

    public function formatCep(string $cep): ?string
    {
        $unformatted = preg_replace('/[^0-9]/', '', $cep);

        if (strlen((string) $unformatted) !== 8) {
            return null;
        }

        return preg_replace('/(\d{5})(\d{3})/', '$1-$2', (string) $unformatted);
    }

    public function formatPlate(string $plate): ?string
    {
        $unformatted = preg_replace('/[^A-Z0-9]/', '', $plate);

        if (strlen((string) $unformatted) !== 7) {
            return null;
        }

        return preg_replace('/([A-Z]{3})(\d{4})/', '$1-$2', (string) $unformatted);
    }
}

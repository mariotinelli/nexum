<?php

declare(strict_types = 1);

namespace App\Services\Cnpj\Entities;

use Illuminate\Support\Stringable;

class Customer
{
    public function __construct(
        public string $name,
        public string $phone,
        public string $email,
        public string $nickname,
        public array $partners,
        public Address $address,
    ) {
    }

    public static function createFromApi(array $data): self
    {
        $partners = Partner::createFromList($data['socios'] ?? []);

        return new self(
            name: data_get($data, 'razao_social', ''),
            phone: self::formatPhone($data),
            email: data_get($data, 'estabelecimento.email', '') ?? '',
            nickname: data_get($data, 'estabelecimento.nome_fantasia', '') ?? '',
            partners: Partner::toArray($partners),
            address: Address::createFromApi($data),
        );
    }

    protected static function formatPhone(array $data): string
    {
        $ddd   = data_get($data, 'estabelecimento.ddd1', '');
        $phone = data_get($data, 'estabelecimento.telefone1', '');

        return str($phone)
            ->whenNotEmpty(fn (Stringable $str) => $str->substrReplace('-', 4, 0))
            ->prepend($ddd)
            ->substrReplace('(', 0, 0)
            ->substrReplace(')', 3, 0)
            ->substrReplace(' ', 4, 0)
            ->toString();
    }
}

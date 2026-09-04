<?php

declare(strict_types = 1);

namespace App\Services\Cnpj\Entities;

use App\Models;

readonly class Address
{
    public function __construct(
        public string $cityName,
        public string $stateName,
        public int $cityId,
        public string $street,
        public string $number,
        public string $district,
        public ?string $complement,
        public string $postalCode,
    ) {
    }

    public static function createFromApi(array $data): self
    {
        $cityName = data_get($data, 'estabelecimento.cidade.nome', '');

        $city = Models\City::query()->firstWhere('name', $cityName);

        return new self(
            cityName: $cityName ?? '',
            stateName: data_get($data, 'estabelecimento.estado.nome', '') ?? '',
            cityId: $city->id ?? 0,
            street: data_get($data, 'estabelecimento.logradouro', '') ?? '',
            number: data_get($data, 'estabelecimento.numero', '') ?? '',
            district: data_get($data, 'estabelecimento.bairro', '') ?? '',
            complement: data_get($data, 'estabelecimento.complemento', '') ?? '',
            postalCode: self::getPostalCode(data_get($data, 'estabelecimento.cep', '')),
        );
    }

    protected static function getPostalCode(string $postalCode): string
    {
        return str($postalCode)
            ->substrReplace('-', 5, 0)
            ->toString();
    }

    public function toModel(?Models\Address $address): Models\Address
    {
        $address ??= new Models\Address();

        $address->street      = $this->street;
        $address->number      = $this->number;
        $address->district    = $this->district;
        $address->postal_code = $this->postalCode;
        $address->city_id     = $this->cityId;

        return $address;
    }
}

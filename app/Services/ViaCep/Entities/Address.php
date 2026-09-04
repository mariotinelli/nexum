<?php

declare(strict_types = 1);

namespace App\Services\ViaCep\Entities;

use App\Models\Address as AddressModel;
use App\Models\City;

class Address
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
        $city = City::where('name', $data['localidade'])->first();

        return new self(
            cityName: $data['localidade'] ?? '',
            stateName: $data['uf'] ?? '',
            cityId: $city->id ?? 0,
            street: $data['logradouro'] ?? '',
            number: $data['unidade'] ?? '',
            district: $data['bairro'] ?? '',
            complement: $data['complemento'] ?? '',
            postalCode: $data['cep'] ?? '',
        );
    }

    public function toModel(?AddressModel $address = null): AddressModel
    {
        $address ??= new AddressModel();

        $address->city_id     = $this->cityId;
        $address->street      = $this->street;
        $address->number      = $this->number;
        $address->district    = $this->district;
        $address->complement  = $this->complement;
        $address->postal_code = $this->postalCode;

        return $address;
    }
}

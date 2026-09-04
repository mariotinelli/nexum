<?php

declare(strict_types = 1);

use App\Models\Address as AddressModel;
use App\Models\City;
use App\Services\Cnpj\Entities\Address;

it('creates cnpj address from api and formats postal code', function (): void {
    $city = City::factory()->create(['name' => 'Sao Paulo']);

    $address = Address::createFromApi([
        'estabelecimento' => [
            'cidade'      => ['nome' => 'Sao Paulo'],
            'estado'      => ['nome' => 'SP'],
            'logradouro'  => 'Rua A',
            'numero'      => '100',
            'bairro'      => 'Centro',
            'complemento' => 'Sala 1',
            'cep'         => '12345678',
        ],
    ]);

    expect($address->cityId)->toBe($city->id)
        ->and($address->postalCode)->toBe('12345-678')
        ->and($address->street)->toBe('Rua A');
});

it('maps cnpj entity data to address model', function (): void {
    $entity = new Address(
        cityName: 'City',
        stateName: 'ST',
        cityId: 10,
        street: 'Street',
        number: '20',
        district: 'District',
        complement: null,
        postalCode: '99999-999',
    );

    $model = $entity->toModel(new AddressModel());

    expect($model->street)->toBe('Street')
        ->and($model->number)->toBe('20')
        ->and($model->district)->toBe('District')
        ->and($model->postal_code)->toBe('99999-999')
        ->and($model->city_id)->toBe(10);
});

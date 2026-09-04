<?php

declare(strict_types = 1);

use App\Models\Address as AddressModel;
use App\Models\City;
use App\Services\ViaCep\Entities\Address;

it('creates viacep address entity from api payload', function (): void {
    $city = City::factory()->create(['name' => 'Campinas']);

    $address = Address::createFromApi([
        'localidade'  => 'Campinas',
        'uf'          => 'SP',
        'logradouro'  => 'Rua C',
        'unidade'     => '20',
        'bairro'      => 'Centro',
        'complemento' => 'Apto 2',
        'cep'         => '13000-000',
    ]);

    expect($address->cityId)->toBe($city->id)
        ->and($address->street)->toBe('Rua C')
        ->and($address->postalCode)->toBe('13000-000');
});

it('maps viacep address entity data to address model', function (): void {
    $entity = new Address(
        cityName: 'Campinas',
        stateName: 'SP',
        cityId: 33,
        street: 'Rua D',
        number: '40',
        district: 'Centro',
        complement: 'Casa',
        postalCode: '13000-001',
    );

    $model = $entity->toModel(new AddressModel());

    expect($model->city_id)->toBe(33)
        ->and($model->street)->toBe('Rua D')
        ->and($model->number)->toBe('40')
        ->and($model->district)->toBe('Centro')
        ->and($model->complement)->toBe('Casa')
        ->and($model->postal_code)->toBe('13000-001');
});

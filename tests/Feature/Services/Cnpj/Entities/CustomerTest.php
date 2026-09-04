<?php

declare(strict_types = 1);

use App\Models\City;
use App\Services\Cnpj\Entities\Customer;

it('creates customer entity from api payload', function (): void {
    City::factory()->create(['name' => 'Sao Paulo']);

    $customer = Customer::createFromApi([
        'razao_social' => 'Empresa LTDA',
        'socios'       => [
            ['nome' => 'Socio 1', 'cpf_cnpj_socio' => '1'],
        ],
        'estabelecimento' => [
            'ddd1'          => '11',
            'telefone1'     => '99998888',
            'email'         => 'empresa@example.com',
            'nome_fantasia' => 'Empresa',
            'cidade'        => ['nome' => 'Sao Paulo'],
            'estado'        => ['nome' => 'SP'],
            'logradouro'    => 'Rua B',
            'numero'        => '10',
            'bairro'        => 'Centro',
            'complemento'   => '',
            'cep'           => '01001000',
        ],
    ]);

    expect($customer->name)->toBe('Empresa LTDA')
        ->and($customer->phone)->toBe('(11) 9999-8888')
        ->and($customer->partners)->toBe([
            ['name' => 'Socio 1', 'document' => '1'],
        ])
        ->and($customer->address->cityName)->toBe('Sao Paulo');
});

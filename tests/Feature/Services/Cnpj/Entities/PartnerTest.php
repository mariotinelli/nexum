<?php

declare(strict_types = 1);

use App\Services\Cnpj\Entities\Partner;

it('creates partner from api payload', function (): void {
    $partner = Partner::createFromApi([
        'nome'           => 'Maria Partner',
        'cpf_cnpj_socio' => '12345678900',
    ]);

    expect($partner->name)->toBe('Maria Partner')
        ->and($partner->document)->toBe('12345678900');
});

it('creates partners from list and converts to array', function (): void {
    $partners = Partner::createFromList([
        ['nome' => 'A', 'cpf_cnpj_socio' => '1'],
        ['nome' => 'B', 'cpf_cnpj_socio' => '2'],
    ]);

    expect($partners)->toHaveCount(2)
        ->and(Partner::toArray($partners))->toBe([
            ['name' => 'A', 'document' => '1'],
            ['name' => 'B', 'document' => '2'],
        ]);
});

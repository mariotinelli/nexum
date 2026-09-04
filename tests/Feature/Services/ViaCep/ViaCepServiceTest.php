<?php

declare(strict_types = 1);

use App\Models\City;
use App\Services\ViaCep\Entities\Address;
use App\Services\ViaCep\Exceptions\BadRequestException;
use App\Services\ViaCep\Exceptions\CepNotFoundException;
use App\Services\ViaCep\ViaCepService;
use Illuminate\Support\Facades\Http;

it('throws bad request for status 400', function (): void {
    Http::fake(['*' => Http::response([], 400)]);

    expect(fn () => (new ViaCepService())->getAddress('13000-000'))->toThrow(BadRequestException::class);
});

it('throws cep not found when api returns erro true', function (): void {
    Http::fake(['*' => Http::response(['erro' => 'true'], 200)]);

    expect(fn () => (new ViaCepService())->getAddress('13000-000'))->toThrow(CepNotFoundException::class);
});

it('returns address entity when api payload is valid', function (): void {
    $city = City::factory()->create(['name' => 'Campinas']);

    Http::fake(['*' => Http::response([
        'localidade'  => 'Campinas',
        'uf'          => 'SP',
        'logradouro'  => 'Rua E',
        'unidade'     => '15',
        'bairro'      => 'Centro',
        'complemento' => '',
        'cep'         => '13000-000',
    ], 200)]);

    $address = (new ViaCepService())->getAddress('13000-000');

    expect($address)->toBeInstanceOf(Address::class)
        ->and($address->cityId)->toBe($city->id)
        ->and($address->street)->toBe('Rua E');
});

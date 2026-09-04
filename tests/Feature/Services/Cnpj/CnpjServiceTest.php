<?php

declare(strict_types = 1);

use App\Services\Cnpj\CnpjService;
use App\Services\Cnpj\Exceptions\CnpjLimitException;
use App\Services\Cnpj\Exceptions\CnpjNotFoundException;
use App\Services\Cnpj\Exceptions\CnpjOutOfServiceException;
use Illuminate\Support\Facades\Http;

it('throws not found exception for 404 or 400 statuses', function (): void {
    Http::fake(['*' => Http::response([], 404)]);
    expect(fn () => (new CnpjService())->getCustomer('12.345.678/0001-90'))->toThrow(CnpjNotFoundException::class);

    Http::fake(['*' => Http::response([], 400)]);
    expect(fn () => (new CnpjService())->getCustomer('12345678000190'))->toThrow(CnpjNotFoundException::class);
});

it('throws limit exception for status 429', function (): void {
    Http::fake(['*' => Http::response([], 429)]);

    expect(fn () => (new CnpjService())->getCustomer('12345678000190'))->toThrow(CnpjLimitException::class);
});

it('throws out of service exception for status 504', function (): void {
    Http::fake(['*' => Http::response([], 504)]);

    expect(fn () => (new CnpjService())->getCustomer('12345678000190'))->toThrow(CnpjOutOfServiceException::class);
});

it('throws not found exception for any other status', function (): void {
    Http::fake(['*' => Http::response([], 200)]);

    expect(fn () => (new CnpjService())->getCustomer('12345678000190'))->toThrow(CnpjNotFoundException::class);
});

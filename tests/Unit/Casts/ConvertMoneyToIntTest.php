<?php

declare(strict_types = 1);

use App\Casts\Money;
use Illuminate\Database\Eloquent\Model;

it('tests get method', function (): void {
    $model = Mockery::mock(Model::class);
    $cast  = new Money();

    $result = $cast->get($model, 'test_key', 10000, []);
    expect($result)->toBe(100.00);

    $result = $cast->get($model, 'test_key', 100.00, []);
    expect($result)->toBe(100.00);

    $result = $cast->get($model, 'test_key', null, []);
    expect($result)->toBeNull();
});

it('tests set method', function (): void {
    $model = Mockery::mock(Model::class);
    $cast  = new Money();

    $result = $cast->set($model, 'test_key', '100,00', []);
    expect($result)->toBe(10000);

    $result = $cast->set($model, 'test_key', null, []);
    expect($result)->toBeNull();
});

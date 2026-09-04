<?php

declare(strict_types = 1);

use App\Models\Address;
use App\Models\City;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

it('returns city relation', function (): void {
    $address = Address::factory()->make();

    expect($address->city())->toBeInstanceOf(BelongsTo::class);
});

it('resolves city through relationship', function (): void {
    $city    = City::factory()->create();
    $address = Address::factory()->create(['city_id' => $city->id]);

    expect($address->city)->toBeInstanceOf(City::class)
        ->and($address->city->id)->toBe($city->id);
});

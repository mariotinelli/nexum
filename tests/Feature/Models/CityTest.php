<?php

declare(strict_types = 1);

use App\Models\Address;
use App\Models\City;
use App\Models\State;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

it('returns city relationships and timestamps flag', function (): void {
    $city = City::factory()->make();

    expect($city->state())->toBeInstanceOf(BelongsTo::class)
        ->and($city->addresses())->toBeInstanceOf(HasMany::class)
        ->and($city->timestamps)->toBeFalse();
});

it('loads state and addresses relationship data', function (): void {
    $state = State::factory()->create();
    $city  = City::factory()->create(['state_id' => $state->id]);

    Address::factory()->count(2)->create(['city_id' => $city->id]);

    expect($city->state)->toBeInstanceOf(State::class)
        ->and($city->addresses)->toHaveCount(2);
});

<?php

declare(strict_types = 1);

use App\Models\City;
use App\Models\Region;
use App\Models\State;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

it('returns state relationships and timestamps flag', function (): void {
    $state = State::factory()->make();

    expect($state->region())->toBeInstanceOf(BelongsTo::class)
        ->and($state->cities())->toBeInstanceOf(HasMany::class)
        ->and($state->timestamps)->toBeFalse();
});

it('loads region and cities from relationship', function (): void {
    $region = Region::factory()->create();
    $state  = State::factory()->create(['region_id' => $region->id]);

    City::factory()->count(2)->create(['state_id' => $state->id]);

    expect($state->region)->toBeInstanceOf(Region::class)
        ->and($state->cities)->toHaveCount(2);
});

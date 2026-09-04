<?php

declare(strict_types = 1);

use App\Models\Region;
use App\Models\State;
use Illuminate\Database\Eloquent\Relations\HasMany;

it('returns states relationship and timestamps flag', function (): void {
    $region = Region::factory()->make();

    expect($region->states())->toBeInstanceOf(HasMany::class)
        ->and($region->timestamps)->toBeFalse();
});

it('loads states from relationship', function (): void {
    $region = Region::factory()->create();
    State::factory()->count(2)->create(['region_id' => $region->id]);

    expect($region->states)->toHaveCount(2);
});

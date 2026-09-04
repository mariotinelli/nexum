<?php

declare(strict_types = 1);

namespace Database\Factories;

use App\Models\Region;
use Illuminate\Database\Eloquent\Factories\Factory;

class StateFactory extends Factory
{
    public function definition(): array
    {
        return [
            'name'      => $this->faker->state(),
            'initials'  => $this->faker->stateAbbr(),
            'region_id' => Region::factory(),
        ];
    }
}

<?php

declare(strict_types = 1);

namespace Database\Factories;

use App\Models\Role;
use Illuminate\Database\Eloquent\Factories\Factory;

class RoleFactory extends Factory
{
    public function definition(): array
    {
        return [
            'name'        => $this->faker->word(),
            'description' => $this->faker->text(),
        ];
    }

    public function withPermissions(array $permissions = []): self
    {
        return $this->afterCreating(function (Role $role) use ($permissions): void {
            $role->givePermissionTo($permissions);
        });
    }
}

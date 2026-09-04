<?php

declare(strict_types = 1);

use App\Models\Role;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

it('returns users relation', function (): void {
    $role = Role::factory()->make();

    expect($role->users())->toBeInstanceOf(HasMany::class);
});

it('returns permissions relation from trait', function (): void {
    $role = Role::factory()->make();

    expect($role->permissions())->toBeInstanceOf(BelongsToMany::class);
});

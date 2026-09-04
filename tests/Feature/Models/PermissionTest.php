<?php

declare(strict_types = 1);

use App\Models\Permission;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

it('returns users relation', function (): void {
    $permission = Permission::factory()->make();

    expect($permission->users())->toBeInstanceOf(BelongsToMany::class);
});

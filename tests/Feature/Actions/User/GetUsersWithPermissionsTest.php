<?php

declare(strict_types = 1);

use App\Actions\User\GetUsersWithPermissions;
use App\Models\Permission;
use App\Models\Role;
use App\Models\User;

it('returns admin users and users with at least one requested permission', function (): void {
    $requestedPermission = Permission::factory()->create([
        'name' => 'permission-requested-' . fake()->uuid(),
    ]);

    $otherPermission = Permission::factory()->create([
        'name' => 'permission-other-' . fake()->uuid(),
    ]);

    $roleWithPermission = Role::factory()->create();
    $roleWithPermission->permissions()->attach($requestedPermission->id);

    $roleWithoutPermission = Role::factory()->create();
    $roleWithoutPermission->permissions()->attach($otherPermission->id);

    $adminUser         = User::factory()->admin()->create();
    $allowedUser       = User::factory()->user()->create(['role_id' => $roleWithPermission->id]);
    $userWithoutAccess = User::factory()->user()->create(['role_id' => $roleWithoutPermission->id]);
    $userWithoutRole   = User::factory()->user()->create(['role_id' => null]);

    $users = (new GetUsersWithPermissions())->handle([$requestedPermission->name]);

    expect($users->pluck('id')->all())
        ->toContain($adminUser->id, $allowedUser->id)
        ->not->toContain($userWithoutAccess->id, $userWithoutRole->id)
        ->and($users->every(fn (User $user): bool => $user instanceof User))->toBeTrue();
});

it('returns only admin users when requested permissions are empty', function (): void {
    $permission = Permission::factory()->create([
        'name' => 'permission-empty-request-' . fake()->uuid(),
    ]);

    $role = Role::factory()->create();
    $role->permissions()->attach($permission->id);

    $adminUser  = User::factory()->admin()->create();
    $normalUser = User::factory()->user()->create(['role_id' => $role->id]);

    $users = (new GetUsersWithPermissions())->handle([]);

    expect($users->pluck('id')->all())
        ->toContain($adminUser->id)
        ->not->toContain($normalUser->id)
        ->and($users)->toHaveCount(1);
});

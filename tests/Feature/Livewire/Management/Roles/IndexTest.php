<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\RolePermissions;
use App\Livewire\Admin\Management\Roles\Index;
use App\Models\Role;

use function Pest\Livewire\livewire;

beforeEach(function (): void {
    actingAsUser(RolePermissions::View);
});

it('can access with view roles permission', function (): void {
    $user = actingAsUser(RolePermissions::View);
    $user->revokePermissionTo(RolePermissions::View);

    livewire(Index::class)
        ->assertForbidden();

    $user->givePermissionTo(RolePermissions::View);

    livewire(Index::class)
        ->assertOk();
});

it('can list all roles', function (): void {
    $roles = Role::factory()
        ->count(3)
        ->create()
        ->sortByDesc('id');

    livewire(Index::class)
        ->assertSet('roles', function ($data) use ($roles): true {
            expect($data)
                ->toHaveCount(3 + 1) // +1 for the default role
                ->first()->name->toBe($roles->first()->name);

            return true;
        });
});

it('can search role by name', function (): void {
    $roles = Role::factory()
        ->count(2)
        ->sequence(
            ['name' => 'Administrator'],
            ['name' => 'Cliente'],
        )
        ->create();

    livewire(Index::class)
        ->set('search', 'Administrator')
        ->assertSet('roles', function ($data) use ($roles): true {
            expect($data)
                ->toHaveCount(1)
                ->first()->name->toBe($roles->first()->name);

            return true;
        });
});

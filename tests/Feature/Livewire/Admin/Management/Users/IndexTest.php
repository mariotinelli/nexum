<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\UserPermissions;
use App\Enums\Status;
use App\Enums\TypeUsers;
use App\Livewire\Admin\Management\Users\Index;
use App\Models\Role;
use App\Models\User;

use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->user = actingAsUser(UserPermissions::View);

    $this->roleAdmin = Role::factory()->create(['name' => 'Admin']);
    $this->roleUser  = Role::factory()->create(['name' => 'User']);

    $this->users = User::factory()
        ->count(5)
        ->sequence(
            ['name' => 'Alice', 'type' => TypeUsers::User->value, 'role_id' => $this->roleAdmin->id],
            ['name' => 'Bob', 'type' => TypeUsers::User->value, 'role_id' => $this->roleUser->id],
            ['name' => 'Charlie', 'type' => TypeUsers::User->value, 'role_id' => $this->roleUser->id],
            ['name' => 'Dave', 'type' => TypeUsers::Admin->value, 'role_id' => $this->roleAdmin->id],
            ['name' => 'Eve', 'type' => TypeUsers::User->value, 'role_id' => $this->roleAdmin->id],
        )
        ->create()
        ->sortBy('name');
});

it('can access with view users permission', function (): void {
    $this->user->revokePermissionTo(UserPermissions::View);

    livewire(Index::class)
        ->assertForbidden();

    $this->user->givePermissionTo(UserPermissions::View);

    livewire(Index::class)
        ->assertOk();
});

it('can list all users filtered by type User', function (): void {
    livewire(Index::class)
        ->assertSet('users', function ($paginator): bool {
            $items = collect($paginator->items());

            $types      = $items->pluck('type')->sort()->values()->toArray();
            $otherTypes = [TypeUsers::Admin->value, TypeUsers::Customer->value];

            expect($paginator->total())->toBe(5)
                ->and($types)->not->toContain($otherTypes);

            return true;
        });
});

it('can search users by name', function (): void {
    livewire(Index::class)
        ->set('search', 'Alice')
        ->assertSet('users', function ($paginator): bool {
            $items = collect($paginator->items());

            expect($items)->toHaveCount(1)
                ->and($items->first()->name)->toBe('Alice');

            return true;
        });
});

it('can filter users by roles', function (): void {
    livewire(Index::class)
        ->set('filters.roles', [$this->roleAdmin->id])
        ->assertSet('users', function ($paginator): bool {
            $items = collect($paginator->items());

            $names = $items->pluck('name')->sort()->values()->toArray();

            expect($paginator->total())->toBe(2)
                ->and($names)->toMatchArray(['Alice', 'Eve']);

            return true;
        });
});

it('can filter users by status', function (): void {
    $userToDeactivate = $this->users->first();
    $userToDeactivate->delete();

    livewire(Index::class)
        ->set('filters.status', Status::Deactivated->value)
        ->assertSet('users', function ($paginator) use ($userToDeactivate): bool {
            $items = collect($paginator->items());

            expect($paginator->total())->toBe(1)
                ->and($items->first()->id)->toBe($userToDeactivate->id);

            return true;
        });

    livewire(Index::class)
        ->set('filters.status', Status::Active->value)
        ->assertSet('users', function ($paginator) use ($userToDeactivate): bool {
            $items = collect($paginator->items());

            expect($items->pluck('id'))->not->toContain($userToDeactivate->id);

            return true;
        });
});

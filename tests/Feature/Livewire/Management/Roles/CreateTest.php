<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\RolePermissions;
use App\Livewire\Admin\Management\Roles\Create;
use App\Models\Permission;
use App\Models\Role;

use function Pest\Laravel\assertDatabaseCount;
use function Pest\Laravel\assertDatabaseHas;
use function Pest\Livewire\livewire;

beforeEach(function (): void {
    actingAsUser(RolePermissions::Create);
});

it('can access with create roles permission', function (): void {
    $user = actingAsUser(RolePermissions::Create);

    $user->revokePermissionTo(RolePermissions::Create);

    livewire(Create::class)
        ->call('loadRole')
        ->assertForbidden();

    $user->givePermissionTo(RolePermissions::Create);

    livewire(Create::class)
        ->call('loadRole')
        ->assertOk();
});

it('can create a role', function (): void {
    $selectedPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value);

    livewire(Create::class)
        ->call('loadRole')
        ->set('role.name', 'Admin')
        ->set('role.description', 'Test role')
        ->set('selectedPermissions', $selectedPermissions->toArray())
        ->call('save')
        ->assertHasNoErrors()
        ->assertToast('Perfil cadastrado com sucesso')
        ->assertDispatched('roles::refresh');

    assertDatabaseHas('roles', [
        'name'        => 'Admin',
        'description' => 'Test role',
    ]);

    $role        = Role::query()->latest('id')->first();
    $permissions = Permission::query()->whereIn('name', $selectedPermissions->toArray())->get();

    assertDatabaseCount('permission_role', $permissions->count() + 1); // +1 for the default role

    foreach ($permissions as $permission) {
        assertDatabaseHas('permission_role', [
            'role_id'       => $role->id,
            'permission_id' => $permission->id,
        ]);
    }
});

it('can load permission from selected template', function (): void {
    $template            = Role::factory()->create();
    $selectedPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value)->toArray();
    $template->syncPermissions($selectedPermissions);

    assertDatabaseCount('permission_role', $template->permissions()->count() + 1); // +1 for the default role

    livewire(Create::class)
        ->call('loadRole')
        ->set('template', $template->id)
        ->assertDispatched('select-template')
        ->assertSet('selectedPermissions', fn ($data): true => count(array_diff($data, $selectedPermissions)) === 0
            && count(array_diff($selectedPermissions, $data)) === 0);
});

it('can clear permissions when clear template', function (): void {
    $template            = Role::factory()->create();
    $selectedPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value)->toArray();
    $template->syncPermissions($selectedPermissions);

    assertDatabaseCount('permission_role', $template->permissions()->count() + 1); // +1 for the default role

    livewire(Create::class)
        ->call('loadRole')
        ->set('template', $template->id)
        ->assertDispatched('select-template')
        ->assertSet('selectedPermissions', fn ($data): true => count(array_diff($data, $selectedPermissions)) === 0
            && count(array_diff($selectedPermissions, $data)) === 0)
        ->set('template', null)
        ->assertSet('selectedPermissions', [])
        ->assertDispatched('select-template', []);
});

it('validate name', function ($name, $rule): void {
    livewire(Create::class)
        ->call('loadRole')
        ->set('role.name', $name)
        ->call('save')
        ->assertHasErrors(['role.name' => $rule]);
})->with([
    [null, 'required'],
    [123, 'string'],
    ['ab', 'min'],
    [str_repeat('a', 192), 'max'],
]);

it('validate description', function ($description, $rule): void {
    livewire(Create::class)
        ->call('loadRole')
        ->set('role.description', $description)
        ->call('save')
        ->assertHasErrors(['role.description' => $rule]);
})->with([
    [123, 'string'],
    ['ab', 'min'],
    [str_repeat('a', 501), 'max'],
]);

it('validate selected permissions', function ($permissions, $field, $rule): void {
    livewire(Create::class)
        ->call('loadRole')
        ->set('selectedPermissions', $permissions)
        ->call('save')
        ->assertHasErrors([$field => $rule]);
})->with([
    [null, 'selectedPermissions', 'required'],
    [['invalid'], 'selectedPermissions.0', 'exists'],
]);

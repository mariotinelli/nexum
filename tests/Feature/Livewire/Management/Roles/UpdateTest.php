<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\RolePermissions;
use App\Livewire\Admin\Management\Roles\Update;
use App\Models\Permission;
use App\Models\Role;

use function Pest\Laravel\assertDatabaseCount;
use function Pest\Laravel\assertDatabaseHas;
use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->user = actingAsUser(RolePermissions::Edit);

    $this->role = Role::factory()->create();
});

it('can access with edit roles permission', function (): void {
    $this->user->revokePermissionTo(RolePermissions::Edit);

    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->assertForbidden();

    $this->user->givePermissionTo(RolePermissions::Edit);

    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->assertOk();
});

it('can load role correctly', function (): void {
    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->assertSet('role.name', $this->role->name)
        ->assertSet('role.description', $this->role->description)
        ->assertSet('selectedPermissions', $this->role->permissions->pluck('name')->toArray());
});

it('can update a role', function (): void {
    $selectedPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value)->toArray();
    $this->role->syncPermissions($selectedPermissions);

    assertDatabaseCount('permission_role', $this->role->permissions()->count() + 1); // +1 for the default role

    $newPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value);

    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->set('role.name', 'Admin')
        ->set('role.description', 'Test role')
        ->set('selectedPermissions', $newPermissions->toArray())
        ->call('save')
        ->assertHasNoErrors()
        ->assertToast('Perfil atualizado com sucesso')
        ->assertDispatched('roles::refresh');

    assertDatabaseHas('roles', [
        'id'          => $this->role->id,
        'name'        => 'Admin',
        'description' => 'Test role',
    ]);

    $permissions = Permission::query()->whereIn('name', $newPermissions->toArray())->get();

    assertDatabaseCount('permission_role', $permissions->count() + 1); // +1 for the default role

    foreach ($permissions as $permission) {
        assertDatabaseHas('permission_role', [
            'role_id'       => $this->role->id,
            'permission_id' => $permission->id,
        ]);
    }
});

it('can load permission from selected template', function (): void {
    $template            = Role::factory()->create();
    $selectedPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value)->toArray();
    $template->syncPermissions($selectedPermissions);

    assertDatabaseCount('permission_role', $template->permissions()->count() + 1); // +1 for the default role

    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->set('template', $template->id)
        ->assertSet('selectedPermissions', fn ($data): true => count(array_diff($data, $selectedPermissions)) === 0
            && count(array_diff($selectedPermissions, $data)) === 0);
});

it('can clear permissions when clear template', function (): void {
    $template            = Role::factory()->create();
    $selectedPermissions = collect(RolePermissions::all())->map(fn (RolePermissions $permission) => $permission->value)->toArray();
    $template->syncPermissions($selectedPermissions);

    assertDatabaseCount('permission_role', $template->permissions()->count() + 1); // +1 for the default role

    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->set('template', $template->id)
        ->assertDispatched('select-template')
        ->assertSet('selectedPermissions', fn ($data): true => count(array_diff($data, $selectedPermissions)) === 0
            && count(array_diff($selectedPermissions, $data)) === 0)
        ->set('template', null)
        ->assertSet('selectedPermissions', [])
        ->assertDispatched('select-template', []);
});

it('validate name', function ($name, $rule): void {
    livewire(Update::class)
        ->call('loadRole', $this->role->id)
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
    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->set('role.description', $description)
        ->call('save')
        ->assertHasErrors(['role.description' => $rule]);
})->with([
    [123, 'string'],
    ['ab', 'min'],
    [str_repeat('a', 501), 'max'],
]);

it('validate selected permissions', function ($permissions, $field, $rule): void {
    livewire(Update::class)
        ->call('loadRole', $this->role->id)
        ->set('selectedPermissions', $permissions)
        ->call('save')
        ->assertHasErrors([$field => $rule]);
})->with([
    [null, 'selectedPermissions', 'required'],
    [['invalid'], 'selectedPermissions.0', 'exists'],
]);

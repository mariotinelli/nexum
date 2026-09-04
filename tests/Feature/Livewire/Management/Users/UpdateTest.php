<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\UserPermissions;
use App\Enums\TypeUsers;
use App\Livewire\Admin\Management\Users\Update;
use App\Models\Role;
use App\Models\User;

use function Pest\Laravel\assertDatabaseHas;
use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->user = actingAsUser(UserPermissions::Edit);

    $role = Role::factory()->create();

    $this->userToEdit = User::factory()->create([
        'name'    => 'John Doe',
        'email'   => '8YH2R@example.com',
        'type'    => TypeUsers::User->value,
        'role_id' => $role->id,
    ]);
});

it('cannot access update component without edit permission', function (): void {
    $this->user->revokePermissionTo(UserPermissions::Edit);

    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->assertForbidden();

    $this->user->givePermissionTo(UserPermissions::Edit);

    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->assertOk();
});

it('can load user data into the component', function (): void {
    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->assertSet('user.name', $this->userToEdit->name)
        ->assertSet('user.email', $this->userToEdit->email)
        ->assertSet('user.role_id', $this->userToEdit->role_id)
        ->assertSet('modalOpen', true);
});

it('can update user data successfully', function (): void {
    $targetRole = Role::factory()->create();

    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->set('user.name', 'Updated Name')
        ->set('user.email', 'updated@example.com')
        ->set('user.role_id', $targetRole->id)
        ->call('save')
        ->assertHasNoErrors()
        ->assertToast('Usuário atualizado com sucesso')
        ->assertDispatched('users::refresh')
        ->assertSet('modalOpen', false);

    assertDatabaseHas('users', [
        'id'      => $this->userToEdit->id,
        'name'    => 'Updated Name',
        'email'   => 'updated@example.com',
        'type'    => TypeUsers::User->value,
        'role_id' => $targetRole->id,
    ]);
});

test('name validation', function ($name, $rule): void {
    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->set('user.name', $name)
        ->call('save')
        ->assertHasErrors(['user.name' => $rule]);
})->with([
    [null, 'required'],
    [154, 'string'],
    [str_repeat('a', 192), 'max'],
    ['aa', 'min'],
]);

test('email validation', function ($email, $rule): void {
    User::factory()->create(['email' => 'existing@example.com']);

    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->set('user.email', $email)
        ->call('save')
        ->assertHasErrors(['user.email' => $rule]);
})->with([
    [null, 'required'],
    ['invalid-email', 'email'],
    [str_repeat('a', 192) . '@gmail.com', 'max'],
    ['existing@example.com', 'unique'],
]);

test('role_id validation', function ($roleId, $rule): void {
    livewire(Update::class)
        ->call('loadUser', $this->userToEdit->id)
        ->set('user.role_id', $roleId)
        ->call('save')
        ->assertHasErrors(['user.role_id' => $rule]);
})->with([
    [null, 'required'],
]);

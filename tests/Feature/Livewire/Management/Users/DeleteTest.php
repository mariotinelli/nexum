<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\UserPermissions;
use App\Enums\TypeUsers;
use App\Livewire\Admin\Management\Users\Delete;
use App\Models\Role;
use App\Models\User;

use function Pest\Laravel\assertSoftDeleted;
use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->loggedUser = actingAsUser(UserPermissions::Delete);

    $this->role = Role::factory()->create();

    $this->user = User::factory()->create([
        'name'    => 'User To Delete',
        'type'    => TypeUsers::User->value,
        'role_id' => $this->role->id,
    ]);
});

it('can delete with user permission', function (): void {
    $this->loggedUser->revokePermissionTo(UserPermissions::Delete);

    livewire(Delete::class)
        ->call('loadUser', $this->user->id)
        ->assertForbidden();

    $this->loggedUser->givePermissionTo(UserPermissions::Delete);

    livewire(Delete::class)
        ->call('loadUser', $this->user->id)
        ->assertOk();
});

it('can load user data into the delete component and open modal', function (): void {
    livewire(Delete::class)
        ->call('loadUser', $this->user->id)
        ->assertSet('user.id', $this->user->id)
        ->assertSet('modalOpen', true);
});

it('can delete a user', function (): void {
    livewire(Delete::class)
        ->call('loadUser', $this->user->id)
        ->assertSet('modalOpen', true)
        ->call('delete')
        ->assertSet('modalOpen', false)
        ->assertToast('Usuário desativado com sucesso');

    assertSoftDeleted($this->user);
});

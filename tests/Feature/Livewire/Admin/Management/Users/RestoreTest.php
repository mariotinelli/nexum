<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\UserPermissions;
use App\Enums\TypeUsers;
use App\Livewire\Admin\Management\Users\Restore;
use App\Models\Role;
use App\Models\User;

use function Pest\Laravel\assertNotSoftDeleted;
use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->loggedUser = actingAsUser(UserPermissions::Restore);

    $this->role = Role::factory()->create();

    $this->userToRestore = User::factory()->create([
        'name'    => 'User To Restore',
        'type'    => TypeUsers::User->value,
        'role_id' => $this->role->id,
    ]);

    $this->userToRestore->delete();
});

it('can access with restore user permission', function (): void {
    $this->loggedUser->revokePermissionTo(UserPermissions::Restore);

    livewire(Restore::class)
        ->call('loadUser', $this->userToRestore->id)
        ->assertForbidden();

    $this->loggedUser->givePermissionTo(UserPermissions::Restore);

    livewire(Restore::class)
        ->call('loadUser', $this->userToRestore->id)
        ->assertOk();
});

it('can restore a soft deleted user successfully', function (): void {
    livewire(Restore::class)
        ->call('loadUser', $this->userToRestore->id)
        ->assertSet('modalOpen', true)
        ->call('restore')
        ->assertDispatched('users::refresh')
        ->assertToast('Usuário ativado com sucesso')
        ->assertSet('modalOpen', false);

    assertNotSoftDeleted($this->userToRestore);
});

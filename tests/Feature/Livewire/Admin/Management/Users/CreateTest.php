<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\UserPermissions;
use App\Enums\TypeUsers;
use App\Livewire\Admin\Management\Users\Create;
use App\Models\Role;
use App\Models\User;
use App\Notifications\NewUserNotification;
use Illuminate\Support\Facades\Notification;

use function Pest\Laravel\assertDatabaseHas;
use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->user = actingAsUser(UserPermissions::Create);
});

it('can access with create user permission', function (): void {
    $this->user->revokePermissionTo(UserPermissions::Create);

    livewire(Create::class)
        ->call('loadUser')
        ->assertForbidden();

    $this->user->givePermissionTo(UserPermissions::Create);

    livewire(Create::class)
        ->call('loadUser')
        ->assertOk();
});

it('can create a user', function (): void {
    Notification::fake();

    $role = Role::factory()->create();

    livewire(Create::class)
        ->call('loadUser')
        ->assertSet('modalOpen', true)
        ->set('user', [
            'name'    => 'John Doe',
            'email'   => '8YH2R@example.com',
            'role_id' => $role->id,
        ])
        ->call('save')
        ->assertHasNoErrors()
        ->assertToast('Usuário cadastrado com sucesso')
        ->assertDispatched('users::refresh')
        ->assertSet('modalOpen', false);

    $newUser = User::query()->where('email', '8YH2R@example.com')->first();

    expect($newUser)->not->toBeNull()
        ->and($newUser->type)->toBe(TypeUsers::User)
        ->and($newUser->role_id)->toBe($role->id);

    assertDatabaseHas('users', [
        'email'   => '8YH2R@example.com',
        'name'    => 'John Doe',
        'type'    => TypeUsers::User->value,
        'role_id' => $role->id,
    ]);

    Notification::assertSentTo($newUser, NewUserNotification::class);
});

test('name', function ($name, $rule): void {
    livewire(Create::class)
        ->call('loadUser')
        ->set('user.name', $name)
        ->call('save')
        ->assertHasErrors(['user.name' => $rule]);
})->with([
    [null, 'required'],
    [154, 'string'],
    [str_repeat('a', 192), 'max'],
    ['aa', 'min'],
]);

test('email', function ($email, $rule): void {
    User::factory()->create(['email' => '8YH2R@example.com']);

    livewire(Create::class)
        ->call('loadUser')
        ->set('user.email', $email)
        ->call('save')
        ->assertHasErrors(['user.email' => $rule]);
})->with([
    [null, 'required'],
    ['aaa123', 'email'],
    [str_repeat('a', 192) . '@gmail.com', 'max'],
    ['8YH2R@example.com', 'unique'],
]);

test('role_id', function ($roleId, $rule): void {
    livewire(Create::class)
        ->call('loadUser')
        ->set('user.role_id', $roleId)
        ->call('save')
        ->assertHasErrors(['user.role_id' => $rule]);
})->with([
    [null, 'required'],
]);

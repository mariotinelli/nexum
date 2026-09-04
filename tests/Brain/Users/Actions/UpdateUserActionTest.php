<?php

declare(strict_types = 1);

use App\Brain\Users\Actions\UpdateUserAction;
use App\Enums\TypeUsers;
use App\Models\Role;
use App\Models\User;
use Illuminate\Validation\ValidationException;

use function Pest\Laravel\assertDatabaseHas;

it('updates user fields with valid payload', function (): void {
    $originalRole = Role::factory()->create();
    $targetRole   = Role::factory()->create();

    $user = User::factory()->user()->create([
        'name'    => 'Before',
        'email'   => 'before.user.task@example.com',
        'role_id' => $originalRole->id,
    ]);

    UpdateUserAction::dispatchSync([
        'user'     => $user,
        'userData' => [
            'name'    => 'After',
            'email'   => 'after.user.task@example.com',
            'type'    => TypeUsers::User,
            'role_id' => $targetRole->id,
        ],
    ]);

    assertDatabaseHas('users', [
        'id'      => $user->id,
        'name'    => 'After',
        'email'   => 'after.user.task@example.com',
        'type'    => TypeUsers::User->value,
        'role_id' => $targetRole->id,
    ]);
});

it('validates unique email when updating user', function (): void {
    User::factory()->create(['email' => 'duplicated.update.task@example.com']);

    $role = Role::factory()->create();
    $user = User::factory()->user()->create([
        'email'   => 'current.update.task@example.com',
        'role_id' => $role->id,
    ]);

    expect(fn () => UpdateUserAction::dispatchSync([
        'user'     => $user,
        'userData' => [
            'name'    => $user->name,
            'email'   => 'duplicated.update.task@example.com',
            'type'    => TypeUsers::User,
            'role_id' => $role->id,
        ],
    ]))->toThrow(ValidationException::class);
});

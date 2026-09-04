<?php

declare(strict_types = 1);

use App\Brain\Users\Actions\CreateUserAction;
use App\Enums\TypeUsers;
use App\Models\Role;
use App\Models\User;
use Brain\Actions\Events\Processing;
use Brain\SensitiveValue;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

use function Pest\Laravel\assertDatabaseHas;

it('creates user with provided password and role', function (): void {
    $role = Role::factory()->create();

    /** @var CreateUserAction $task */
    $task = CreateUserAction::dispatchSync([
        'userData' => [
            'name'    => 'John Doe',
            'email'   => 'john.doe.task@example.com',
            'type'    => TypeUsers::User,
            'role_id' => $role->id,
        ],
        'password' => 'Secret@123',
    ]);

    expect($task->user)
        ->toBeInstanceOf(User::class)
        ->and($task->user->name)->toBe('John Doe')
        ->and($task->user->email)->toBe('john.doe.task@example.com')
        ->and($task->user->type)->toBe(TypeUsers::User)
        ->and($task->user->role_id)->toBe($role->id)
        ->and(Hash::check('Secret@123', $task->user->password))->toBeTrue();

    assertDatabaseHas('users', [
        'id'      => $task->user->id,
        'name'    => 'John Doe',
        'email'   => 'john.doe.task@example.com',
        'type'    => TypeUsers::User->value,
        'role_id' => $role->id,
    ]);
});

it('creates user with null role', function (): void {
    /** @var CreateUserAction $task */
    $task = CreateUserAction::dispatchSync([
        'userData' => [
            'name'  => 'Mary Smith',
            'email' => 'mary.smith.task@example.com',
            'type'  => TypeUsers::Admin,
        ],
        'password' => 'Admin@123',
    ]);

    expect($task->user)
        ->toBeInstanceOf(User::class)
        ->and($task->user->name)->toBe('Mary Smith')
        ->and($task->user->email)->toBe('mary.smith.task@example.com')
        ->and($task->user->type)->toBe(TypeUsers::Admin)
        ->and($task->user->role_id)->toBeNull()
        ->and(Hash::check('Admin@123', $task->user->password))->toBeTrue();

    assertDatabaseHas('users', [
        'id'      => $task->user->id,
        'name'    => 'Mary Smith',
        'email'   => 'mary.smith.task@example.com',
        'type'    => TypeUsers::Admin->value,
        'role_id' => null,
    ]);
});

it('validates unique email when creating user', function (): void {
    User::factory()->create([
        'email' => 'duplicated@example.com',
    ]);

    expect(fn () => CreateUserAction::dispatchSync([
        'userData' => [
            'name'  => 'Other User',
            'email' => 'duplicated@example.com',
            'type'  => TypeUsers::User,
        ],
        'password' => 'Secret@123',
    ]))->toThrow(ValidationException::class);
});

it('requires a password', function (): void {
    expect(fn () => CreateUserAction::dispatchSync([
        'userData' => [
            'name'  => 'Passwordless User',
            'email' => 'passwordless@example.com',
            'type'  => TypeUsers::User,
        ],
    ]))->toThrow(ValidationException::class);
});

it('redacts the password from Brain events', function (): void {
    Event::fake([Processing::class]);

    CreateUserAction::dispatchSync([
        'userData' => [
            'name'  => 'Sensitive User',
            'email' => 'sensitive@example.com',
            'type'  => TypeUsers::User,
        ],
        'password' => 'Sensitive@123',
    ]);

    Event::assertDispatched(Processing::class, fn (Processing $event): bool => $event->payload->password instanceof SensitiveValue
        && (string) $event->payload->password === '**********'
        && json_decode((string) json_encode($event->payload), true)['password'] === '**********');
});

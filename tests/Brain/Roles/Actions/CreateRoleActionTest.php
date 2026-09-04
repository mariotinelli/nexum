<?php

declare(strict_types = 1);

use App\Brain\Roles\Actions\CreateRoleAction;
use App\Enums\Permissions\Management\RolePermissions;
use App\Models\Role;
use Illuminate\Validation\ValidationException;

use function Pest\Laravel\assertDatabaseHas;

it('creates role with selected permissions', function (): void {
    /** @var CreateRoleAction $task */
    $task = CreateRoleAction::dispatchSync([
        'roleData' => [
            'name'        => 'Perfil Task Create',
            'description' => 'Descrição de teste',
        ],
        'selectedPermissions' => [
            RolePermissions::View->value,
            RolePermissions::Create->value,
        ],
    ]);

    expect($task->role)
        ->toBeInstanceOf(Role::class)
        ->and($task->role->name)->toBe('Perfil Task Create')
        ->and($task->role->description)->toBe('Descrição de teste')
        ->and($task->role->hasPermissionTo(RolePermissions::View))->toBeTrue()
        ->and($task->role->hasPermissionTo(RolePermissions::Create))->toBeTrue();

    assertDatabaseHas('roles', [
        'id'          => $task->role->id,
        'name'        => 'Perfil Task Create',
        'description' => 'Descrição de teste',
    ]);
});

it('validates permission names when creating role', function (): void {
    expect(fn () => CreateRoleAction::dispatchSync([
        'roleData' => [
            'name' => 'Perfil Inválido',
        ],
        'selectedPermissions' => ['invalid-permission'],
    ]))->toThrow(ValidationException::class);
});

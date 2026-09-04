<?php

declare(strict_types = 1);

use App\Brain\Roles\Actions\UpdateRoleAction;
use App\Enums\Permissions\Management\RolePermissions;
use App\Models\Role;
use Illuminate\Validation\ValidationException;

use function Pest\Laravel\assertDatabaseHas;

it('updates role data and sync permissions', function (): void {
    $role = Role::factory()->create([
        'name'        => 'Perfil Original',
        'description' => 'Descrição original',
    ]);

    $role->syncPermissions([RolePermissions::View->value]);

    UpdateRoleAction::dispatchSync([
        'role'     => $role,
        'roleData' => [
            'name'        => 'Perfil Atualizado',
            'description' => 'Descrição atualizada',
        ],
        'selectedPermissions' => [
            RolePermissions::Edit->value,
        ],
    ]);

    $role->refresh();

    expect($role->name)->toBe('Perfil Atualizado')
        ->and($role->description)->toBe('Descrição atualizada')
        ->and($role->hasPermissionTo(RolePermissions::Edit))->toBeTrue()
        ->and($role->hasPermissionTo(RolePermissions::View))->toBeFalse();

    assertDatabaseHas('roles', [
        'id'          => $role->id,
        'name'        => 'Perfil Atualizado',
        'description' => 'Descrição atualizada',
    ]);
});

it('validates permission names when updating role', function (): void {
    $role = Role::factory()->create();

    expect(fn () => UpdateRoleAction::dispatchSync([
        'role'     => $role,
        'roleData' => [
            'name'        => $role->name,
            'description' => $role->description,
        ],
        'selectedPermissions' => ['invalid-permission'],
    ]))->toThrow(ValidationException::class);
});

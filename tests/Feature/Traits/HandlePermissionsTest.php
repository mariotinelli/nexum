<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\UserPermissions;
use App\Models\Permission;
use App\Models\Role;
use Illuminate\Support\Facades\Cache;

function forceRunningInConsole(bool $value): void
{
    $property = new ReflectionProperty(app(), 'isRunningInConsole');
    $property->setAccessible(true);
    $property->setValue(app(), $value);
}

it('attaches a single permission to role', function (): void {
    Permission::query()->firstOrCreate(['name' => UserPermissions::View->value]);

    $role = Role::factory()->create();
    $role->givePermissionTo(UserPermissions::View);

    expect($role->permissions()->pluck('name')->all())->toContain(UserPermissions::View->value);
});

it('attaches many permissions to role', function (): void {
    Permission::query()->firstOrCreate(['name' => UserPermissions::Create->value]);
    Permission::query()->firstOrCreate(['name' => UserPermissions::Edit->value]);

    $role = Role::factory()->create();
    $role->givePermissionTo([UserPermissions::Create, UserPermissions::Edit]);

    expect($role->permissions()->pluck('name')->all())
        ->toContain(UserPermissions::Create->value, UserPermissions::Edit->value);
});

it('does nothing when giving empty permission set', function (): void {
    $role = Role::factory()->create();

    $role->givePermissionTo([]);

    expect($role->permissions()->count())->toBe(0);
});

it('checks if role has permission', function (): void {
    Permission::query()->firstOrCreate(['name' => UserPermissions::Delete->value]);

    $role = Role::factory()->create();
    $role->givePermissionTo(UserPermissions::Delete);

    expect($role->hasPermissionTo(UserPermissions::Delete))->toBeTrue()
        ->and($role->hasPermissionTo(UserPermissions::Restore))->toBeFalse();
});

it('checks permission using cache branch when not running in console', function (): void {
    $role = Role::factory()->create();

    forceRunningInConsole(false);

    Cache::shouldReceive('remember')
        ->once()
        ->with($role->getKeyPermissionCache(), Mockery::type(DateTimeInterface::class), Mockery::type(Closure::class))
        ->andReturn([UserPermissions::View->value]);

    expect($role->hasPermissionTo(UserPermissions::View))->toBeTrue();

    forceRunningInConsole(true);
});

it('syncs permissions by permission names', function (): void {
    Permission::query()->firstOrCreate(['name' => UserPermissions::View->value]);
    Permission::query()->firstOrCreate(['name' => UserPermissions::Create->value]);

    $role = Role::factory()->create();
    $role->syncPermissions([UserPermissions::View->value, UserPermissions::Create->value]);

    expect($role->permissions()->pluck('name')->all())
        ->toContain(UserPermissions::View->value, UserPermissions::Create->value);
});

it('returns permission cache key using role id', function (): void {
    $role = Role::factory()->create();

    expect($role->getKeyPermissionCache())->toBe("role::{$role->id}::permissions");
});

it('revokes one and many permissions from role', function (): void {
    Permission::query()->firstOrCreate(['name' => UserPermissions::View->value]);
    Permission::query()->firstOrCreate(['name' => UserPermissions::Create->value]);

    $role = Role::factory()->create();
    $role->givePermissionTo([UserPermissions::View, UserPermissions::Create]);

    $role->revokePermissionTo(UserPermissions::View);
    expect($role->permissions()->pluck('name')->all())->not->toContain(UserPermissions::View->value);

    $role->revokePermissionTo([UserPermissions::Create]);
    expect($role->permissions()->pluck('name')->all())->not->toContain(UserPermissions::Create->value);
});

it('does nothing when revoking empty permission set', function (): void {
    $role = Role::factory()->create();

    $role->revokePermissionTo([]);

    expect($role->permissions()->count())->toBe(0);
});

it('refreshes permission cache when app is not running unit tests', function (): void {
    $role = Role::factory()->create();

    app()->instance('env', 'local');

    Cache::shouldReceive('forget')->once()->with($role->getKeyPermissionCache());
    Cache::shouldReceive('remember')
        ->once()
        ->with($role->getKeyPermissionCache(), Mockery::type(DateTimeInterface::class), Mockery::type(Closure::class))
        ->andReturn([]);

    $role->refreshPermissionCache();

    app()->instance('env', 'testing');
});

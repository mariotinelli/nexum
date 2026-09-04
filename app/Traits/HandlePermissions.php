<?php

declare(strict_types = 1);

namespace App\Traits;

use App\Models\Permission;
use BackedEnum;
use DateTimeInterface;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Support\Facades\Cache;

trait HandlePermissions
{
    private function rememberUntil(): DateTimeInterface
    {
        return now()->addMinutes(5);
    }

    public function permissions(): BelongsToMany
    {
        return $this->belongsToMany(Permission::class);
    }

    /**
     * @param  BackedEnum|array<BackedEnum>  $permission
     */
    public function givePermissionTo(BackedEnum | array $permission): void
    {
        if (empty($permission)) {
            return;
        }

        $permissions = Permission::query()
            ->when(
                is_array($permission),
                fn ($query) => $query->whereIn('name', array_map(fn (BackedEnum $perm) => $perm->value, $permission)),
                fn ($query) => $query->where('name', $permission->value)
            )->get();

        $this->permissions()->attach($permissions);

        $this->refreshPermissionCache();
    }

    public function hasPermissionTo(BackedEnum $permission): bool
    {
        /** @var array<int, string> $permissions */
        $permissions = app()->runningInConsole()
            ? $this->permissions()->pluck('name')->all()
            : Cache::remember(
                $this->getKeyPermissionCache(),
                $this->rememberUntil(),
                fn (): array => $this->permissions()->pluck('name')->all()
            );

        return in_array($permission->value, $permissions, true);
    }

    public function syncPermissions(array $permissions): void
    {
        $permissions = Permission::query()
            ->select('id')
            ->whereIn('name', $permissions)
            ->pluck('id')
            ->toArray();

        $this->permissions()->sync($permissions);

        $this->refreshPermissionCache();
    }

    public function getKeyPermissionCache(): string
    {
        return "role::{$this->id}::permissions";
    }

    public function revokePermissionTo(BackedEnum | array $permission): void
    {
        if (empty($permission)) {
            return;
        }

        $permissions = Permission::query()
            ->when(
                is_array($permission),
                fn ($query) => $query->whereIn('name', array_map(fn (BackedEnum $perm) => $perm->value, $permission)),
                fn ($query) => $query->where('name', $permission->value)
            )->get();

        $this->permissions()->detach($permissions);

        $this->refreshPermissionCache();
    }

    public function refreshPermissionCache(): void
    {
        if (app()->runningUnitTests()) {
            return;
        }

        Cache::forget($this->getKeyPermissionCache());
        Cache::remember(
            $this->getKeyPermissionCache(),
            $this->rememberUntil(),
            fn (): array => $this->permissions()->pluck('name')->all()
        );
    }
}

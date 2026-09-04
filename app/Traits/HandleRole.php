<?php

declare(strict_types = 1);

namespace App\Traits;

use App\Enums\TypeUsers;
use App\Models\Role;
use BackedEnum;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

trait HandleRole
{
    public function role(): BelongsTo
    {
        return $this->belongsTo(Role::class);
    }

    public function hasPermissionTo(BackedEnum $permission): bool
    {
        if (!$this->role) {
            return false;
        }

        if ($this->type === TypeUsers::Admin) {
            return true;
        }

        return $this->role->hasPermissionTo($permission);
    }

    public function givePermissionTo(BackedEnum | array $permission): void
    {
        if (empty($permission) || !$this->role) {
            return;
        }

        $this->role->givePermissionTo($permission);
    }

    public function revokePermissionTo(BackedEnum | array $permission): void
    {
        if (empty($permission) || !$this->role) {
            return;
        }

        $this->role->revokePermissionTo($permission);
    }
}

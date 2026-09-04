<?php

declare(strict_types = 1);

namespace App\Policies;

use App\Enums\Permissions\Management\RolePermissions;
use App\Models\Role;
use App\Models\User;
use App\Traits\Policies\CheckIsAdmin;

class RolePolicy
{
    use CheckIsAdmin;

    public function viewAny(User $user): bool
    {
        return $user->hasPermissionTo(RolePermissions::View);
    }

    public function create(User $user): bool
    {
        return $user->hasPermissionTo(RolePermissions::Create);
    }

    public function update(User $user, Role $role): bool
    {
        return $user->hasPermissionTo(RolePermissions::Edit);
    }
}

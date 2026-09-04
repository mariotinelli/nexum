<?php

declare(strict_types = 1);

namespace App\Policies;

use App\Enums\Permissions\Management\UserPermissions;
use App\Models\User;

class UserPolicy
{
    public function viewAny(User $user): bool
    {
        return $user->isAdmin() || $user->hasPermissionTo(UserPermissions::View);
    }

    public function create(User $user): bool
    {
        return $user->isAdmin() || $user->hasPermissionTo(UserPermissions::Create);
    }

    public function update(User $user, User $model): bool
    {
        return $user->isAdmin() || $user->hasPermissionTo(UserPermissions::Edit);
    }

    public function delete(User $user, User $model): bool
    {
        return $user->isAdmin() || $user->hasPermissionTo(UserPermissions::Delete);
    }

    public function restore(User $user, User $model): bool
    {
        return $user->isAdmin() || $user->hasPermissionTo(UserPermissions::Restore);
    }

    public function viewAnyProject(User $user): bool
    {
        return $user->isCustomer();
    }
}

<?php

declare(strict_types = 1);

namespace App\Actions\User;

use App\Enums\TypeUsers;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Collection;

class GetUsersWithPermissions
{
    public function handle(array $permissions): Collection
    {
        return User::query()
            ->whereType(TypeUsers::Admin->value)
            ->orWhereHas('role.permissions', fn (Builder $query) => $query->whereIn('name', $permissions))
            ->get();
    }
}

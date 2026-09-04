<?php

declare(strict_types = 1);

namespace App\Actions;

use App\Enums\TypeUsers;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;

class GetAdmins
{
    public function handle(): Collection
    {
        return User::query()
            ->where('type', TypeUsers::Admin->value)
            ->get();
    }
}

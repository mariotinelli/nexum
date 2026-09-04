<?php

declare(strict_types = 1);

namespace App\Enums;

use App\Enums\Permissions\Management\RolePermissions;
use App\Enums\Permissions\Management\UserPermissions;

enum Can: string
{
    public static function allCases(): array
    {
        return [
            ...RolePermissions::cases(),
            ...UserPermissions::cases(),
            ...self::cases(),
        ];
    }

    public static function management(): array
    {
        return [
            'roles' => (object) [
                'label'       => 'Perfis',
                'permissions' => RolePermissions::all(),
            ],
            'users' => (object) [
                'label'       => 'Usuários',
                'permissions' => UserPermissions::all(),
            ],
        ];
    }

    public static function groups(): array
    {
        return [
            'management' => (object) [
                'label' => 'Gestão',
                'group' => Can::management(),
            ],
        ];
    }
}

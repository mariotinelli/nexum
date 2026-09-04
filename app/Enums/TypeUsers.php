<?php

declare(strict_types = 1);

namespace App\Enums;

enum TypeUsers: int
{
    case Admin          = 1;
    case User           = 2;
    case Customer       = 3;
    case SupportRemSoft = 4;

    public function label(): string
    {
        return match ($this) {
            self::Admin          => 'Administrador',
            self::User           => 'Usuário',
            self::Customer       => 'Cliente',
            self::SupportRemSoft => 'Suporte Rem Soft',
        };
    }

    public function canAccessAdminArea(): bool
    {
        return in_array($this, [
            self::Admin,
            self::User,
            self::SupportRemSoft,
        ], true);
    }

    /**
     * @return array<int, int>
     */
    public static function adminAreaValues(): array
    {
        return array_values(array_map(
            static fn (self $type): int => $type->value,
            array_filter(self::cases(), static fn (self $type): bool => $type->canAccessAdminArea()),
        ));
    }

    public static function toArray(): array
    {
        return [
            self::Admin->value          => 'Administrador',
            self::User->value           => 'Usuário',
            self::Customer->value       => 'Cliente',
            self::SupportRemSoft->value => 'Suporte Rem Soft',
        ];
    }
}

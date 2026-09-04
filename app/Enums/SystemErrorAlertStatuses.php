<?php

declare(strict_types = 1);

namespace App\Enums;

enum SystemErrorAlertStatuses: int
{
    case Open         = 1;
    case Acknowledged = 2;
    case Resolved     = 3;

    public function label(): string
    {
        return match ($this) {
            self::Open         => 'Aberto',
            self::Acknowledged => 'Reconhecido',
            self::Resolved     => 'Resolvido',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::Open         => 'error',
            self::Acknowledged => 'warning',
            self::Resolved     => 'success',
        };
    }

    public static function options(): array
    {
        return collect(self::cases())->mapWithKeys(fn (self $status): array => [
            $status->value => $status->label(),
        ])->toArray();
    }
}

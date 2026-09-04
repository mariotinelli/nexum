<?php

declare(strict_types = 1);

namespace App\Enums;

enum SystemErrorAlertSeverities: int
{
    case Critical  = 1;
    case Alert     = 2;
    case Emergency = 3;

    public function label(): string
    {
        return match ($this) {
            self::Critical  => 'Crítico',
            self::Alert     => 'Alerta',
            self::Emergency => 'Emergência',
        };
    }

    public function color(): string
    {
        return match ($this) {
            self::Critical  => 'error',
            self::Alert     => 'warning',
            self::Emergency => 'error',
        };
    }

    public static function options(): array
    {
        return collect(self::cases())->mapWithKeys(fn (self $severity): array => [
            $severity->value => $severity->label(),
        ])->toArray();
    }
}

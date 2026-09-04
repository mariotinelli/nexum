<?php

declare(strict_types = 1);

use App\Models\User;
use Illuminate\Support\Number;

function user(): ?User
{
    if (auth()->check()) {
        return auth()->user();
    }

    return null;
}

function withEnvBar(): bool
{
    if (app()->environment('local', 'testing')) {
        return true;
    }

    if (!app()->environment('qa')) {
        return false;
    }

    return request()->cookie('qa_envbar_enabled') === '1';
}

function currency(float | int | string | null $value): string
{
    if (is_string($value)) {
        $value = str($value)
            ->replace('.', '')
            ->replace(',', '.')
            ->toFloat();
    }

    return Number::currency($value ?? 0, in: 'BRL', locale: config('app.locale'));
}

function percentage(float | int | null $value): string
{
    return Number::percentage($value ?? 0);
}

function defaultStatuses(): array
{
    return [
        1 => 'Ativo',
        0 => 'Inativo',
    ];
}

function compareMoney(float | int | string | null $oldValue, float | int | string | null $newValue, string $operator = '!=='): bool
{
    return match ($operator) {
        '!=='   => currency($oldValue) !== currency($newValue),
        default => currency($oldValue) === currency($newValue),
    };
}

<?php

declare(strict_types = 1);

namespace App\Traits\Components;

use Carbon\Carbon;

trait WithConverters
{
    protected function converterRangeToDates(string | null $value, string $fromFormat = 'd/m/Y'): ?array
    {
        if (blank($value)) {
            return null;
        }

        $dates = str($value)->explode(' até ')->toArray();

        if (count($dates) === 0) {
            return null;
        }

        return [
            Carbon::createFromFormat($fromFormat, $dates[0])->startOfDay(),
            Carbon::createFromFormat($fromFormat, $dates[1] ?? $dates[0])->endOfDay(),
        ];
    }

    protected function converterIntToFloat(int | float | null $value): ?float
    {
        if (blank($value) || is_float($value)) {
            return $value;
        }

        return (float) $value / 100;
    }

    protected function converterStringToInt(string | float | int | null $value): ?int
    {
        if (blank($value)) {
            return $value;
        }

        if (is_float($value)) {
            return (int) ($value * 100);
        }

        $floatValue = str($value)
            ->replace('.', '')
            ->replace(',', '.')
            ->toFloat() * 100;

        return (int) $floatValue;
    }

    protected function converterStringToFloat(string | float | int | null $value): ?float
    {
        if (is_string($value) && !str_contains($value, ',') && !str_contains($value, '.')) {
            return $this->converterIntToFloat((int) $value);
        }

        $value = $this->converterStringToInt($value);

        return $this->converterIntToFloat($value);
    }

    protected function converterToFloat(string | float | int $value): float
    {
        return match (true) {
            is_float($value)  => $value,
            is_int($value)    => $this->converterIntToFloat($value),
            is_string($value) => $this->converterStringToFloat($value),
        };
    }
}

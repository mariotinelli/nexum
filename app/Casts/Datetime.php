<?php

declare(strict_types = 1);

namespace App\Casts;

use Carbon\Carbon;
use Illuminate\Contracts\Database\Eloquent\CastsAttributes;
use Illuminate\Database\Eloquent\Model;
use InvalidArgumentException;

class Datetime implements CastsAttributes
{
    public function get(Model $model, string $key, mixed $value, array $attributes): ?Carbon
    {
        return $value ? Carbon::parse($value) : null;
    }

    public function set(Model $model, string $key, mixed $value, array $attributes): mixed
    {
        if (!$value) {
            return null;
        }

        if ($value instanceof Carbon || $value instanceof \DateTime) {
            return $value->format('Y-m-d H:i:s');
        }

        return Carbon::createFromFormat($this->getFormat($value), $value)
            ->format('Y-m-d H:i:s');
    }

    protected function getFormat(mixed $value): string
    {
        $regex = $this->availableRegex();

        return match (true) {
            preg_match($regex['d/m/Y H:i'], (string) $value) === 1 => 'd/m/Y H:i',
            preg_match($regex['d/m/Y'], (string) $value) === 1     => 'd/m/Y',
            preg_match($regex['H:i'], (string) $value) === 1       => 'H:i',
            default                                                => throw new InvalidArgumentException('Invalid datetime format'),
        };
    }

    protected function availableRegex(): array
    {
        return [
            'd/m/Y H:i' => '/^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$/',
            'd/m/Y'     => '/^\d{2}\/\d{2}\/\d{4}$/',
            'H:i'       => '/^\d{2}:\d{2}$/',
        ];
    }
}

<?php

declare(strict_types = 1);

namespace App\Facades;

use App\Actions\BcMath as BcMathAction;
use Illuminate\Support\Facades\Facade;

/**
 * @method static BcMathAction make(float $value)
 */
class BcMath extends Facade
{
    #[\Override]
    protected static function getFacadeAccessor(): string
    {
        return BcMathAction::class;
    }
}

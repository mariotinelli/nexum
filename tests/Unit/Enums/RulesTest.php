<?php

declare(strict_types = 1);

use App\Enums\Rules;

it('returns the money rule order', function (): void {
    expect(Rules::moneyOrder())->toBe([
        'required',
        'between',
        'min',
        'max',
    ]);
});

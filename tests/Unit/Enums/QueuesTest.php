<?php

declare(strict_types = 1);

use App\Enums\Queues;

it('returns all queue values', function (): void {
    expect(Queues::all())->toBe([
        'low_priority',
        'high_priority',
        'long_timeout',
    ]);
});

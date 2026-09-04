<?php

declare(strict_types = 1);

use App\Customs\CustomDispatcher;
use Illuminate\Contracts\Bus\Dispatcher as BusDispatcher;
use Illuminate\Contracts\Bus\QueueingDispatcher;

it('binds bus dispatcher contracts to custom dispatcher', function (): void {
    expect(app(BusDispatcher::class))->toBeInstanceOf(CustomDispatcher::class)
        ->and(app(QueueingDispatcher::class))->toBeInstanceOf(CustomDispatcher::class);
});

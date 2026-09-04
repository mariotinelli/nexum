<?php

declare(strict_types = 1);

namespace App\Providers;

use App\Customs\CustomDispatcher;
use Illuminate\Bus\Dispatcher;
use Illuminate\Container\Container;
use Illuminate\Contracts\Bus\Dispatcher as BusDispatcher;
use Illuminate\Contracts\Bus\QueueingDispatcher;
use Illuminate\Queue\Events\JobProcessing;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\ServiceProvider;
use RuntimeException;

class QueueServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->extend(Dispatcher::class, fn (Dispatcher $dispatcher, Container $app): CustomDispatcher => $this->decorateDispatcher($dispatcher, $app));

        $this->app->extend(BusDispatcher::class, fn (mixed $dispatcher, Container $app): CustomDispatcher => $this->decorateDispatcher($dispatcher, $app));

        $this->app->extend(QueueingDispatcher::class, fn (mixed $dispatcher, Container $app): CustomDispatcher => $this->decorateDispatcher($dispatcher, $app));
    }

    public function boot(): void
    {
        Queue::before(function (JobProcessing $event): void {
            $queueName = (string) $event->job->getQueue();

            Cache::put(
                key: $this->lastProcessedJobCacheKey($event->connectionName, $queueName),
                value: [
                    'connection'  => $event->connectionName,
                    'queue'       => $queueName,
                    'name'        => $event->job->resolveName(),
                    'uuid'        => $event->job->uuid(),
                    'attempts'    => $event->job->attempts(),
                    'reserved_at' => now()->toIso8601String(),
                ],
                ttl: now()->addMinutes(10),
            );
        });
    }

    private function decorateDispatcher(mixed $dispatcher, Container $app): CustomDispatcher
    {
        if ($dispatcher instanceof CustomDispatcher) {
            return $dispatcher;
        }

        if (!$dispatcher instanceof Dispatcher) {
            throw new RuntimeException('Queue dispatcher precisa ser uma instância de Illuminate\\Bus\\Dispatcher.');
        }

        return new CustomDispatcher($app, $dispatcher);
    }

    private function lastProcessedJobCacheKey(string $connection, string $queue): string
    {
        return "alerts:queue:last-job:{$connection}:{$queue}";
    }
}

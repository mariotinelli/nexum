<?php

declare(strict_types = 1);

use App\Enums\Queues;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Queue\Attributes\Queue as QueueAttribute;
use PHPUnit\Framework\ExpectationFailedException;

arch('application code does not use debug helpers')
    ->expect('App')
    ->not->toUse(['dd', 'ds']);

it('ensures notifications are queueable by convention', function (): void {
    $notifications = collect(glob(app_path('Notifications/*.php')));

    expect($notifications)->not->toBeEmpty();

    $notifications->each(function (string $file): void {
        $source = file_get_contents($file);

        if ($source === false) {
            throw new ExpectationFailedException("Unable to read source for {$file}.");
        }

        if (!str_contains($source, 'implements ShouldQueue')) {
            throw new ExpectationFailedException("{$file} must implement " . ShouldQueue::class . '.');
        }

        if (!str_contains($source, 'use Queueable;')) {
            throw new ExpectationFailedException("{$file} must use " . Queueable::class . '.');
        }
    });
});

it('ensures queued jobs and notifications define queue with App\\Enums\\Queues', function (): void {
    $targets = collect([
        ...glob(app_path('Notifications/*.php')),
        ...glob(app_path('Jobs/*.php')),
    ])->map(function (string $file): string {
        return str($file)
            ->replace([app_path() . DIRECTORY_SEPARATOR, app_path() . '/'], 'App\\')
            ->replace([DIRECTORY_SEPARATOR, '/'], '\\')
            ->replace('.php', '')
            ->toString();
    });

    expect($targets)->not->toBeEmpty();

    $targets->each(function (string $className): void {
        $reflection = new ReflectionClass($className);

        if (!$reflection->implementsInterface(ShouldQueue::class)) {
            return;
        }

        $source = file_get_contents($reflection->getFileName());

        if ($source === false) {
            throw new ExpectationFailedException("Unable to read source for {$className}.");
        }

        $queueAttributes = $reflection->getAttributes(QueueAttribute::class);

        if ($queueAttributes === []) {
            throw new ExpectationFailedException("{$className} must define queue via #[Queue(...)] attribute.");
        }

        $sourceUsesQueues = str_contains($source, 'use App\\Enums\\Queues;')
            || str_contains($source, 'App\\Enums\\Queues::');

        if (!$sourceUsesQueues) {
            throw new ExpectationFailedException("{$className} must import or reference App\\Enums\\Queues.");
        }

        $usedQueueCaseNames = [];

        foreach ($queueAttributes as $attribute) {
            $attributeInstance = $attribute->newInstance();
            $queue             = $attributeInstance->queue;

            if ($queue instanceof Queues) {
                $usedQueueCaseNames[] = $queue->name;

                continue;
            }

            if (is_string($queue)) {
                $matchedQueue = collect(Queues::cases())->first(fn (Queues $case): bool => $case->value === $queue);

                if ($matchedQueue instanceof Queues) {
                    $usedQueueCaseNames[] = $matchedQueue->name;

                    continue;
                }
            }

            throw new ExpectationFailedException("{$className} must use App\\Enums\\Queues in #[Queue(...)].");
        }

        preg_match_all('/\$this->onQueue\(\s*Queues::([A-Za-z_][A-Za-z0-9_]*)(?:->value)?\s*\)/', $source, $matches);

        $usedQueueCaseNames    = [...$usedQueueCaseNames, ...($matches[1] ?? [])];
        $allowedQueueCaseNames = array_column(Queues::cases(), 'name');

        foreach ($usedQueueCaseNames as $queueCaseName) {
            if (!in_array($queueCaseName, $allowedQueueCaseNames, true)) {
                throw new ExpectationFailedException("{$className} uses unknown queue case {$queueCaseName}.");
            }
        }

        expect($usedQueueCaseNames)->not->toBeEmpty();
    });
});

it('uses Laravel scope attributes instead of legacy scope-prefixed methods', function (): void {
    $targets = collect([
        ...glob(app_path('Models/*.php')),
        ...glob(app_path('Traits/Models/*.php')),
        ...glob(app_path('Traits/Components/*.php')),
    ]);

    expect($targets)->not->toBeEmpty();

    $targets->each(function (string $file): void {
        $source = file_get_contents($file);

        if ($source === false) {
            throw new ExpectationFailedException("Unable to read source for {$file}.");
        }

        if (preg_match('/function\s+scope[A-Z][A-Za-z0-9_]*\s*\(/', $source) === 1) {
            throw new ExpectationFailedException("{$file} should migrate local scopes to #[Scope] methods.");
        }
    });
});

it('uses Laravel hidden attribute instead of protected $hidden property in models', function (): void {
    $models = collect(glob(app_path('Models/*.php')));

    expect($models)->not->toBeEmpty();

    $models->each(function (string $file): void {
        $source = file_get_contents($file);

        if ($source === false) {
            throw new ExpectationFailedException("Unable to read source for {$file}.");
        }

        if (preg_match('/protected\s+\$hidden\s*=\s*\[/', $source) === 1) {
            throw new ExpectationFailedException("{$file} should migrate hidden configuration to #[Hidden([...])].");
        }
    });
});

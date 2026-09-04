<?php

declare(strict_types = 1);

namespace App\Customs;

use Illuminate\Bus\Dispatcher;
use Illuminate\Contracts\Container\Container;
use Illuminate\Queue\Attributes\Queue as QueueAttribute;
use Illuminate\Queue\Attributes\ReadsQueueAttributes;
use InvalidArgumentException;
use UnitEnum;

class CustomDispatcher extends Dispatcher
{
    use ReadsQueueAttributes;

    private const string DELAY_ATTRIBUTE_CLASS = 'Illuminate\\Queue\\Attributes\\Delay';

    /** @var array<string> */
    private const array FORBIDDEN_QUEUES = ['default'];

    public function __construct(Container $app, Dispatcher $dispatcher)
    {
        parent::__construct($app, $dispatcher->queueResolver);
    }

    public function dispatchToQueue(mixed $command): mixed
    {
        if (!app()->environment(['qa', 'hml', 'homolog', 'prod', 'production'])) {
            return parent::dispatchToQueue($command);
        }

        $queue = $this->resolveQueueName($command);

        if ($queue === null) {
            throw new InvalidArgumentException('A fila não pode estar vazia. Você deve especificar uma fila nomeada.');
        }

        $command->queue = $queue;

        if (in_array($queue, self::FORBIDDEN_QUEUES, true)) {
            throw new InvalidArgumentException("A fila '{$queue}' não é permitida. Você deve especificar uma fila nomeada para todos os jobs.");
        }

        if (!$this->shouldBePrefixed($queue)) {
            return parent::dispatchToQueue($command);
        }

        return $this->prefixAndDispatchToQueue($command);
    }

    protected function shouldBePrefixed(?string $queue): bool
    {
        if (empty($queue)) {
            return false;
        }

        $allowedQueues  = config('queue.prefix.allowed_queues', ['*']);
        $excludedQueues = config('queue.prefix.excluded_queues', []);

        if (in_array($queue, $excludedQueues)) {
            return false;
        }

        if (!in_array($queue, $allowedQueues) && !in_array('*', $allowedQueues)) {
            return false;
        }

        return true;
    }

    protected function prefixAndDispatchToQueue(mixed $command): mixed
    {
        $prefix = config('queue.prefix.value');

        if (empty($prefix)) {
            throw new InvalidArgumentException('O prefixo da fila não pode estar vazio. Você deve definir um prefixo em QUEUE_PREFIX no arquivo env.');
        }

        $command->queue = "{$prefix}_{$command->queue}";

        return parent::dispatchToQueue($command);
    }

    protected function pushCommandToQueue(mixed $queue, mixed $command): mixed
    {
        $resolvedQueue = $this->resolveQueueName($command);
        $prefix        = config('queue.prefix.value');

        if (
            is_string($resolvedQueue)
            && is_string($prefix)
            && $prefix !== ''
            && str_starts_with($resolvedQueue, "{$prefix}_")
        ) {
            $delay = $this->getAttributeValue($command, self::DELAY_ATTRIBUTE_CLASS, 'delay');

            if (isset($delay)) {
                return $queue->later($delay, $command, queue: $resolvedQueue);
            }

            return $queue->push($command, queue: $resolvedQueue);
        }

        return parent::pushCommandToQueue($queue, $command);
    }

    private function resolveQueueName(mixed $command): ?string
    {
        if (!is_object($command)) {
            return null;
        }

        $queue = $command->queue ?? null;

        if ($queue === null || $queue === '') {
            $queue = $this->getAttributeValue($command, QueueAttribute::class, 'queue');
        }

        if ($queue instanceof UnitEnum) {
            return property_exists($queue, 'value') ? (string) $queue->value : $queue->name;
        }

        if (!is_string($queue)) {
            return null;
        }

        $normalizedQueue = trim($queue);

        return $normalizedQueue === '' ? null : $normalizedQueue;
    }
}

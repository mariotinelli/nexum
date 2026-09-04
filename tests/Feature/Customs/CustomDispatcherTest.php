<?php

declare(strict_types = 1);

use App\Customs\CustomDispatcher;
use App\Enums\Queues;
use Illuminate\Bus\Dispatcher;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\Queue;
use Illuminate\Queue\Attributes\Delay;
use Illuminate\Queue\Attributes\Queue as QueueAttribute;

class TestableCustomDispatcher extends CustomDispatcher
{
    public function shouldBePrefixedProxy(?string $queue): bool
    {
        return $this->shouldBePrefixed($queue);
    }
}

function makeCustomDispatcher(Queue $queue): CustomDispatcher
{
    $dispatcher = new Dispatcher(app(), fn (): Queue => $queue);

    return new CustomDispatcher(app(), $dispatcher);
}

it('throws when queue is empty outside local', function (): void {
    app()->detectEnvironment(fn (): string => 'production');

    $command = new class () {
        public ?string $queue = null;
    };

    $queue = Mockery::mock(Queue::class);

    expect(fn () => makeCustomDispatcher($queue)->dispatchToQueue($command))
        ->toThrow(InvalidArgumentException::class, 'A fila não pode estar vazia. Você deve especificar uma fila nomeada.');
});

it('throws when queue is forbidden outside local', function (): void {
    app()->detectEnvironment(fn (): string => 'production');

    $command = new class ('default') {
        public function __construct(public ?string $queue)
        {
        }
    };

    $queue = Mockery::mock(Queue::class);

    expect(fn () => makeCustomDispatcher($queue)->dispatchToQueue($command))
        ->toThrow(InvalidArgumentException::class, "A fila 'default' não é permitida. Você deve especificar uma fila nomeada para todos os jobs.");
});

it('dispatches without prefix when queue should not be prefixed', function (): void {
    app()->detectEnvironment(fn (): string => 'production');
    config()->set('queue.prefix.allowed_queues', ['reports']);
    config()->set('queue.prefix.excluded_queues', ['emails']);
    config()->set('queue.prefix.value', 'app');

    $command = new class ('emails') {
        public function __construct(public ?string $queue)
        {
        }
    };

    $queue = Mockery::mock(Queue::class);
    $queue->shouldReceive('push')
        ->once()
        ->with($command, '', 'emails')
        ->andReturn('queued-no-prefix');

    $result = makeCustomDispatcher($queue)->dispatchToQueue($command);

    expect($result)->toBe('queued-no-prefix')
        ->and($command->queue)->toBe('emails');
});

it('prefixes queue and dispatches when queue is allowed', function (): void {
    app()->detectEnvironment(fn (): string => 'production');
    config()->set('queue.prefix.allowed_queues', ['emails']);
    config()->set('queue.prefix.excluded_queues', []);
    config()->set('queue.prefix.value', 'app');

    $command = new class ('emails') {
        public function __construct(public ?string $queue)
        {
        }
    };

    $queue = Mockery::mock(Queue::class);
    $queue->shouldReceive('push')
        ->once()
        ->with($command, '', 'app_emails')
        ->andReturn('queued-prefixed');

    $result = makeCustomDispatcher($queue)->dispatchToQueue($command);

    expect($result)->toBe('queued-prefixed')
        ->and($command->queue)->toBe('app_emails');
});

it('prefixes jobs with queue attribute enum and keeps prefixed queue on push', function (): void {
    app()->detectEnvironment(fn (): string => 'production');
    config()->set('queue.prefix.allowed_queues', ['high_priority']);
    config()->set('queue.prefix.excluded_queues', []);
    config()->set('queue.prefix.value', 'app');

    $command = new #[QueueAttribute(Queues::HighPriority)] class () {
        use Queueable;
    };

    $queue = Mockery::mock(Queue::class);
    $queue->shouldReceive('push')
        ->once()
        ->with($command, '', 'app_high_priority')
        ->andReturn('queued-prefixed-attribute');

    $result = makeCustomDispatcher($queue)->dispatchToQueue($command);

    expect($result)->toBe('queued-prefixed-attribute')
        ->and($command->queue)->toBe('app_high_priority');
});

it('throws when prefix is empty and queue should be prefixed', function (): void {
    app()->detectEnvironment(fn (): string => 'production');
    config()->set('queue.prefix.allowed_queues', ['*']);
    config()->set('queue.prefix.excluded_queues', []);
    config()->set('queue.prefix.value', null);

    $command = new class ('emails') {
        public function __construct(public ?string $queue)
        {
        }
    };

    $queue = Mockery::mock(Queue::class);

    expect(fn () => makeCustomDispatcher($queue)->dispatchToQueue($command))
        ->toThrow(InvalidArgumentException::class, 'O prefixo da fila não pode estar vazio. Você deve definir um prefixo em QUEUE_PREFIX no arquivo env.');
});

it('evaluates shouldBePrefixed for empty, excluded and not allowed queues', function (): void {
    config()->set('queue.prefix.allowed_queues', ['reports']);
    config()->set('queue.prefix.excluded_queues', ['emails']);

    $dispatcher = new TestableCustomDispatcher(app(), new Dispatcher(app(), fn (): Queue => Mockery::mock(Queue::class)));

    expect($dispatcher->shouldBePrefixedProxy(null))->toBeFalse()
        ->and($dispatcher->shouldBePrefixedProxy('emails'))->toBeFalse()
        ->and($dispatcher->shouldBePrefixedProxy('invoices'))->toBeFalse();
});

it('uses queue later when prefixed queue and delay attribute are present', function (): void {
    app()->detectEnvironment(fn (): string => 'production');
    config()->set('queue.prefix.allowed_queues', ['emails']);
    config()->set('queue.prefix.excluded_queues', []);
    config()->set('queue.prefix.value', 'app');

    $command = new #[QueueAttribute('emails')] #[Delay(30)] class () {
        use Queueable;
    };

    $queue = Mockery::mock(Queue::class);
    $queue->shouldReceive('later')
        ->once()
        ->with(30, $command, '', 'app_emails')
        ->andReturn('queued-later');

    $result = makeCustomDispatcher($queue)->dispatchToQueue($command);

    expect($result)->toBe('queued-later')
        ->and($command->queue)->toBe('app_emails');
});

it('resolves queue name from pure enum using enum name branch', function (): void {
    enum TestQueueEnum
    {
        case Reports;
    }

    app()->detectEnvironment(fn (): string => 'production');
    config()->set('queue.prefix.allowed_queues', ['Reports']);
    config()->set('queue.prefix.excluded_queues', []);
    config()->set('queue.prefix.value', 'app');

    $command = new #[QueueAttribute(TestQueueEnum::Reports)] class () {
        use Queueable;
    };

    $queue = Mockery::mock(Queue::class);
    $queue->shouldReceive('push')
        ->once()
        ->with($command, '', 'app_Reports')
        ->andReturn('queued-enum-name');

    $result = makeCustomDispatcher($queue)->dispatchToQueue($command);

    expect($result)->toBe('queued-enum-name');
});

it('dispatches queue directly on local environment branch', function (): void {
    app()->detectEnvironment(fn (): string => 'local');

    $command = new class ('emails') {
        public function __construct(public ?string $queue)
        {
        }
    };

    $queue = Mockery::mock(Queue::class);
    $queue->shouldReceive('push')
        ->once()
        ->with($command, '', 'emails')
        ->andReturn('queued-local');

    $result = makeCustomDispatcher($queue)->dispatchToQueue($command);

    expect($result)->toBe('queued-local');
});

it('returns null queue name for non object command via reflection', function (): void {
    $dispatcher = makeCustomDispatcher(Mockery::mock(Queue::class));
    $method     = new ReflectionMethod($dispatcher, 'resolveQueueName');
    $method->setAccessible(true);

    expect($method->invoke($dispatcher, 'not-an-object'))->toBeNull();
});

it('resolves queue name from backed enum property value branch', function (): void {
    $dispatcher = makeCustomDispatcher(Mockery::mock(Queue::class));
    $method     = new ReflectionMethod($dispatcher, 'resolveQueueName');
    $method->setAccessible(true);

    $command = new class () {
        public mixed $queue;

        public function __construct()
        {
            $this->queue = Queues::HighPriority;
        }
    };

    expect($method->invoke($dispatcher, $command))->toBe('high_priority');
});

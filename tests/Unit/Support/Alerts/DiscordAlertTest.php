<?php

declare(strict_types = 1);

use App\Enums\Queues;
use App\Enums\SystemErrorAlertSeverities;
use App\Models\SystemErrorAlert;
use App\Support\Alerts\DiscordAlert;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Queue;
use Symfony\Component\HttpKernel\Exception\HttpException;
use Symfony\Component\Process\Exception\ProcessTimedOutException;
use Symfony\Component\Process\Process;

it('sends payload to discord webhook when enabled', function (): void {
    config()->set('alerts.discord.enabled', true);
    config()->set('alerts.discord.webhook_url', 'https://discord.test/webhook');
    config()->set('alerts.discord.timeout', 3);
    config()->set('alerts.discord.retry_times', 1);
    config()->set('alerts.discord.retry_sleep_ms', 1);

    Http::fake([
        'https://discord.test/webhook' => Http::response([], 204),
    ]);

    app(DiscordAlert::class)->send([
        'content' => 'Erro crítico detectado.',
        'embeds'  => [],
    ]);

    Http::assertSent(function ($request): bool {
        return $request->url() === 'https://discord.test/webhook'
            && $request['content'] === 'Erro crítico detectado.';
    });
});

it('does not send payload when discord alerts are disabled', function (): void {
    config()->set('alerts.discord.enabled', false);
    config()->set('alerts.discord.webhook_url', 'https://discord.test/webhook');

    Http::fake();

    app(DiscordAlert::class)->send([
        'content' => 'Erro crítico detectado.',
        'embeds'  => [],
    ]);

    Http::assertNothingSent();
});

it('builds payload with details link to internal UI', function (): void {
    $alert = SystemErrorAlert::factory()->create();

    $payload = app(DiscordAlert::class)->buildPayload($alert);

    $detailsField = collect($payload['embeds'][0]['fields'])
        ->first(fn (array $field): bool => $field['name'] === 'Detalhes');

    expect($detailsField)->not->toBeNull()
        ->and($detailsField['value'])->toContain('/suporte-rem-soft/alertas-erros/');
});

it('stores queue runtime context when a worker timeout is reported', function (): void {
    config()->set('alerts.discord.enabled', true);
    config()->set('alerts.discord.webhook_url', 'https://discord.test/webhook');

    Queue::fake();

    Cache::put('alerts:queue:last-job:database:long_timeout', [
        'connection'  => 'database',
        'queue'       => Queues::LongTimeout->value,
        'name'        => 'App\\Jobs\\ScrapeProjectsSourceJob',
        'uuid'        => 'job-uuid-123',
        'attempts'    => 2,
        'reserved_at' => now()->toIso8601String(),
    ], now()->addMinutes(10));

    $process = new Process([
        'php',
        'artisan',
        'queue:work',
        '--once',
        '--queue=' . Queues::LongTimeout->value,
        '--tries=3',
    ]);
    $process->setTimeout(160);

    $exception = new ProcessTimedOutException($process, ProcessTimedOutException::TYPE_GENERAL);

    app(DiscordAlert::class)->report($exception);

    $alert = SystemErrorAlert::query()->latest('id')->first();

    expect($alert)->not->toBeNull()
        ->and($alert?->context['queue_worker']['queues'])->toContain(Queues::LongTimeout->value)
        ->and($alert?->context['queue_last_jobs'][Queues::LongTimeout->value]['name'])->toBe('App\\Jobs\\ScrapeProjectsSourceJob');
});

it('does not report ignored and 4xx http exceptions', function (): void {
    config()->set('alerts.discord.enabled', true);
    config()->set('alerts.discord.webhook_url', 'https://discord.test/webhook');
    config()->set('alerts.discord.ignored_exceptions', [LogicException::class]);

    $alert = app(DiscordAlert::class);

    $reflection = new ReflectionClass($alert);
    $method     = $reflection->getMethod('shouldReport');
    $method->setAccessible(true);

    $ignored = $method->invoke($alert, new LogicException('ignored'));
    $http4xx = $method->invoke($alert, new HttpException(404, 'not found'));
    $http5xx = $method->invoke($alert, new HttpException(500, 'server error'));

    expect($ignored)->toBeFalse()
        ->and($http4xx)->toBeFalse()
        ->and($http5xx)->toBeTrue();
});

it('skips throttle cache add when throttle is disabled', function (): void {
    config()->set('alerts.discord.throttle_seconds', 0);

    $alert = app(DiscordAlert::class);

    Cache::shouldReceive('add')->never();

    $reflection = new ReflectionClass($alert);
    $method     = $reflection->getMethod('wasRecentlyReported');
    $method->setAccessible(true);

    $result = $method->invoke($alert, 'fingerprint-abc');

    expect($result)->toBeFalse();
});

it('extracts command and queues from timeout messages and sanitizes context', function (): void {
    $alert = app(DiscordAlert::class);

    $reflection = new ReflectionClass($alert);

    $extractCommand = $reflection->getMethod('extractTimedOutCommand');
    $extractCommand->setAccessible(true);

    $extractQueues = $reflection->getMethod('extractQueueNamesFromCommand');
    $extractQueues->setAccessible(true);

    $sanitize = $reflection->getMethod('sanitizeRecursive');
    $sanitize->setAccessible(true);

    $process = Process::fromShellCommandline('php artisan queue:work --queue=default,' . Queues::LongTimeout->value . ',default');
    $process->setTimeout(10);

    $timeoutException = new ProcessTimedOutException($process, ProcessTimedOutException::TYPE_GENERAL);

    $command = $extractCommand->invoke($alert, $timeoutException);
    $queues  = $extractQueues->invoke($alert, $command);

    $emptyQueues  = $extractQueues->invoke($alert, 'php artisan queue:work --once');
    $quotedQueues = $extractQueues->invoke($alert, "'php' 'artisan' 'queue:work' '--queue=" . Queues::LongTimeout->value . "' '--once'");

    $sanitized = $sanitize->invoke($alert, [
        'token'  => 'abc',
        'nested' => [
            'authorization' => 'Bearer x',
            'name'          => 'ok',
        ],
    ]);

    expect($command)->toContain('--queue=default,' . Queues::LongTimeout->value . ',default')
        ->and($queues)->toBe(['default', Queues::LongTimeout->value])
        ->and($emptyQueues)->toBe([])
        ->and($quotedQueues)->toBe([Queues::LongTimeout->value])
        ->and($sanitized['token'])->toBe('**********')
        ->and($sanitized['nested']['authorization'])->toBe('**********')
        ->and($sanitized['nested']['name'])->toBe('ok');
});

it('builds trace summary and formats user fallbacks', function (): void {
    config()->set('alerts.discord.trace_lines', 1);

    $alert = app(DiscordAlert::class);

    $reflection = new ReflectionClass($alert);

    $traceSummary = $reflection->getMethod('buildTraceSummary');
    $traceSummary->setAccessible(true);

    $formatUser = $reflection->getMethod('formatUser');
    $formatUser->setAccessible(true);

    $emptySummary = $traceSummary->invoke($alert, '');
    $limited      = $traceSummary->invoke($alert, "line-1\nline-2");

    $userWithEmail = new class () {
        public function getAuthIdentifier(): int
        {
            return 42;
        }

        public string $email = 'dev@remsoft.com';
    };

    $userWithoutEmail = new class () {
        public function getAuthIdentifier(): int
        {
            return 7;
        }
    };

    $formattedNull         = $formatUser->invoke($alert, null);
    $formattedWithEmail    = $formatUser->invoke($alert, $userWithEmail);
    $formattedWithoutEmail = $formatUser->invoke($alert, $userWithoutEmail);

    expect($emptySummary)->toBe('Rastreio indisponível.')
        ->and($limited)->toBe('line-1')
        ->and($formattedNull)->toBe('Não autenticado')
        ->and($formattedWithEmail)->toBe('42 (dev@remsoft.com)')
        ->and($formattedWithoutEmail)->toBe('7');
});

it('builds sanitized context from request and handles null request', function (): void {
    $alert = app(DiscordAlert::class);

    $reflection = new ReflectionClass($alert);
    $method     = $reflection->getMethod('buildSanitizedContext');
    $method->setAccessible(true);

    $request = Request::create('/x?secret=123&name=ok', 'POST', [
        'password'              => 'hidden',
        'password_confirmation' => 'hidden-2',
        'token'                 => 'abc',
        'payload'               => ['x-api-key' => 'k', 'field' => 'value'],
    ]);
    $request->headers->set('User-Agent', 'Pest');

    $withRequest = $method->invoke($alert, $request);
    $nullRequest = $method->invoke($alert, null);

    expect($withRequest['query']['secret'])->toBe('**********')
        ->and($withRequest['request']['token'])->toBe('**********')
        ->and($withRequest['request']['payload']['x-api-key'])->toBe('**********')
        ->and(isset($withRequest['request']['password']))->toBeFalse()
        ->and($nullRequest)->toBe([]);
});

it('resolves emergency severity and formats user without auth identifier', function (): void {
    $alert = app(DiscordAlert::class);

    $reflection = new ReflectionClass($alert);

    $severity = $reflection->getMethod('resolveSeverity');
    $severity->setAccessible(true);

    $formatUser = $reflection->getMethod('formatUser');
    $formatUser->setAccessible(true);

    $emergency = $severity->invoke($alert, new HttpException(503, 'unavailable'));

    $plainUser = (object) ['email' => 'no-id@remsoft.com'];
    $formatted = $formatUser->invoke($alert, $plainUser);

    expect($emergency)->toBe(SystemErrorAlertSeverities::Emergency)
        ->and($formatted)->toBe('N/A (no-id@remsoft.com)');
});

it('keeps queue last jobs empty when cache value is not array', function (): void {
    config()->set('alerts.discord.enabled', true);
    config()->set('alerts.discord.webhook_url', 'https://discord.test/webhook');

    Queue::fake();

    Cache::put('alerts:queue:last-job:database:long_timeout', 'invalid-value', now()->addMinutes(10));

    $process = new Process([
        'php',
        'artisan',
        'queue:work',
        '--once',
        '--queue=long_timeout',
    ]);
    $process->setTimeout(30);

    app(DiscordAlert::class)->report(new ProcessTimedOutException($process, ProcessTimedOutException::TYPE_GENERAL));

    $alert = SystemErrorAlert::query()->latest('id')->first();

    expect($alert)->not->toBeNull()
        ->and($alert?->context['queue_worker']['queues'])->toBe([Queues::LongTimeout->value])
        ->and($alert?->context['queue_last_jobs'])->toBe([]);
});

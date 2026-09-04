<?php

declare(strict_types = 1);

namespace App\Support\Alerts;

use App\Actions\SystemErrorAlert\UpsertSystemErrorAlert;
use App\Enums\SystemErrorAlertSeverities;
use App\Jobs\SendDiscordCriticalAlertJob;
use App\Models\SystemErrorAlert;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Route;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;
use Symfony\Component\Process\Exception\ProcessTimedOutException;
use Throwable;

class DiscordAlert
{
    /** @param array<string, mixed> $extraContext */
    public function report(Throwable $throwable, array $extraContext = []): void
    {
        if (!$this->shouldReport($throwable)) {
            return;
        }

        $systemErrorAlert = app(UpsertSystemErrorAlert::class)->handle($this->buildUpsertAttributes($throwable, $extraContext));

        if ($this->wasRecentlyReported($systemErrorAlert->fingerprint)) {
            return;
        }

        $systemErrorAlert->update([
            'last_notified_at' => now(),
        ]);

        SendDiscordCriticalAlertJob::dispatch($this->buildPayload($systemErrorAlert));
    }

    public function send(array $payload): void
    {
        $webhookUrl = (string) config('alerts.discord.webhook_url');

        if (!$this->isEnabled() || $webhookUrl === '') {
            return;
        }

        Http::timeout((int) config('alerts.discord.timeout'))
            ->retry((int) config('alerts.discord.retry_times'), (int) config('alerts.discord.retry_sleep_ms'))
            ->post($webhookUrl, [
                'content' => $payload['content'],
                'embeds'  => $payload['embeds'],
            ])
            ->throw();
    }

    /** @return array{content: string, embeds: array<int, array<string, mixed>>} */
    public function buildPayload(SystemErrorAlert $systemErrorAlert): array
    {
        $traceSummary = $this->buildTraceSummary($systemErrorAlert->trace);
        $location     = $this->truncate(($systemErrorAlert->file ?? 'N/A') . ':' . ($systemErrorAlert->line ?? 'N/A'), 1000);
        $alertUrl     = $this->truncate($this->getAlertUrl($systemErrorAlert), 1000);

        return [
            'content' => sprintf(
                '[%s] Erro crítico detectado em %s.',
                strtoupper($systemErrorAlert->environment),
                config('app.name'),
            ),
            'embeds' => [[
                'title'  => 'Exceção crítica do sistema',
                'color'  => 15158332,
                'fields' => [
                    ['name' => 'Exceção', 'value' => $this->truncate($systemErrorAlert->exception_class, 1000), 'inline' => false],
                    ['name' => 'Mensagem', 'value' => $this->truncate($systemErrorAlert->message ?: 'Sem mensagem disponível.', 1000), 'inline' => false],
                    ['name' => 'Local', 'value' => $location, 'inline' => false],
                    ['name' => 'Método', 'value' => $this->truncate($systemErrorAlert->request_method ?? 'N/A', 1000), 'inline' => true],
                    ['name' => 'Rota', 'value' => $this->truncate($systemErrorAlert->route_name ?? 'N/A', 1000), 'inline' => true],
                    ['name' => 'ID da Requisição', 'value' => $this->truncate($systemErrorAlert->request_id ?? 'N/A', 1000), 'inline' => true],
                    ['name' => 'Usuário', 'value' => $this->truncate($this->formatUser($systemErrorAlert->user), 1000), 'inline' => false],
                    ['name' => 'URL', 'value' => $this->truncate($systemErrorAlert->request_url ?? 'N/A', 1000), 'inline' => false],
                    ['name' => 'Ocorrências', 'value' => (string) $systemErrorAlert->occurrences, 'inline' => true],
                    ['name' => 'Detalhes', 'value' => $alertUrl, 'inline' => false],
                    ['name' => 'Rastreio (resumo)', 'value' => $traceSummary, 'inline' => false],
                ],
                'timestamp' => now()->toIso8601String(),
            ]],
        ];
    }

    private function shouldReport(Throwable $throwable): bool
    {
        if (!$this->isEnabled()) {
            return false;
        }

        /** @var array<int, class-string<Throwable>> $ignoredExceptions */
        $ignoredExceptions = config('alerts.discord.ignored_exceptions', []);

        foreach ($ignoredExceptions as $ignoredException) {
            if ($throwable instanceof $ignoredException) {
                return false;
            }
        }

        if ($throwable instanceof HttpExceptionInterface) {
            return $throwable->getStatusCode() >= 500;
        }

        return true;
    }

    private function isEnabled(): bool
    {
        return (bool) config('alerts.discord.enabled') && (string) config('alerts.discord.webhook_url') !== '';
    }

    private function wasRecentlyReported(string $fingerprint): bool
    {
        $throttleSeconds = (int) config('alerts.discord.throttle_seconds', 60);

        if ($throttleSeconds <= 0) {
            return false;
        }

        return !Cache::add("alerts:discord:{$fingerprint}", true, now()->addSeconds($throttleSeconds));
    }

    private function fingerprint(Throwable $throwable, ?Request $request): string
    {
        return hash('sha256', implode('|', [
            $throwable::class,
            $throwable->getMessage(),
            $throwable->getFile(),
            $request?->method() ?? 'N/A',
            $request?->path() ?? 'N/A',
        ]));
    }

    /** @return array<string, mixed> */
    /** @param array<string, mixed> $extraContext */
    private function buildUpsertAttributes(Throwable $throwable, array $extraContext = []): array
    {
        $request        = $this->resolveRequest();
        $trace          = $throwable->getTraceAsString();
        $runtimeContext = $this->buildRuntimeContext($throwable);
        $context        = array_merge(
            $this->buildSanitizedContext($request),
            $runtimeContext,
            $extraContext,
        );

        $isCliRuntime = isset($runtimeContext['queue_worker']) || isset($runtimeContext['queue_last_jobs']);

        return [
            'fingerprint'     => $this->fingerprint($throwable, $request),
            'severity'        => $this->resolveSeverity($throwable),
            'environment'     => app()->environment(),
            'exception_class' => $throwable::class,
            'message'         => $throwable->getMessage() ?: 'Sem mensagem disponível.',
            'file'            => $throwable->getFile(),
            'line'            => $throwable->getLine(),
            'route_name'      => $request?->route()?->getName() ?? $request?->path() ?? ($isCliRuntime ? 'queue-worker' : null),
            'request_method'  => $request?->method() ?? ($isCliRuntime ? 'CLI' : null),
            'request_url'     => $request?->fullUrl() ?? (isset($runtimeContext['queue_worker']['command']) ? (string) $runtimeContext['queue_worker']['command'] : null),
            'request_id'      => $request?->header('X-Request-Id'),
            'user_id'         => Auth::id(),
            'context'         => $context,
            'trace'           => $trace,
            'occurred_at'     => now(),
        ];
    }

    /** @return array<string, mixed> */
    private function buildRuntimeContext(Throwable $throwable): array
    {
        if (!$throwable instanceof ProcessTimedOutException) {
            return [];
        }

        $command = $this->extractTimedOutCommand($throwable);
        $queues  = $this->extractQueueNamesFromCommand($command);

        $lastJobs = [];

        foreach ($queues as $queue) {
            $cacheKey  = "alerts:queue:last-job:database:{$queue}";
            $cachedJob = Cache::get($cacheKey);

            if (!is_array($cachedJob)) {
                continue;
            }

            $lastJobs[$queue] = $cachedJob;
        }

        return [
            'queue_worker' => [
                'command' => $command,
                'queues'  => $queues,
            ],
            'queue_last_jobs' => $lastJobs,
        ];
    }

    private function extractTimedOutCommand(ProcessTimedOutException $throwable): string
    {
        $message = $throwable->getMessage();

        if (preg_match('/The process "(?P<command>.+)" exceeded/', $message, $matches) === 1) {
            return (string) $matches['command'];
        }

        return $message;
    }

    /** @return array<int, string> */
    private function extractQueueNamesFromCommand(string $command): array
    {
        if (preg_match('/--queue=(?P<queues>[^\s\'"]+)/', $command, $matches) !== 1) {
            return [];
        }

        $queueNames = array_filter(array_map(
            static fn (string $queue): string => trim($queue),
            explode(',', (string) $matches['queues']),
        ));

        return array_values(array_unique($queueNames));
    }

    private function resolveRequest(): ?Request
    {
        if (!app()->bound('request')) {
            return null;
        }

        return request();
    }

    private function buildTraceSummary(?string $trace): string
    {
        if (!is_string($trace) || $trace === '') {
            return 'Rastreio indisponível.';
        }

        $traceLines   = explode("\n", $trace);
        $limit        = max((int) config('alerts.discord.trace_lines', 12), 1);
        $traceSummary = implode("\n", array_slice($traceLines, 0, $limit));

        return $this->truncate($traceSummary, 1000);
    }

    private function resolveSeverity(Throwable $throwable): SystemErrorAlertSeverities
    {
        if ($throwable instanceof HttpExceptionInterface && $throwable->getStatusCode() >= 503) {
            return SystemErrorAlertSeverities::Emergency;
        }

        return SystemErrorAlertSeverities::Critical;
    }

    private function getAlertUrl(SystemErrorAlert $systemErrorAlert): string
    {
        if (!app()->bound('router') || !Route::has('admin.support.system-error-alerts.show')) {
            return 'N/A';
        }

        return route('admin.support.system-error-alerts.show', $systemErrorAlert);
    }

    /** @return array<string, mixed> */
    private function buildSanitizedContext(?Request $request): array
    {
        if (!$request) {
            return [];
        }

        return [
            'ip'         => $request->ip(),
            'user_agent' => $request->userAgent(),
            'query'      => $this->sanitizeRecursive($request->query()),
            'request'    => $this->sanitizeRecursive($request->except(['password', 'password_confirmation'])),
        ];
    }

    /** @param array<string, mixed> $data */
    private function sanitizeRecursive(array $data): array
    {
        $sensitiveKeys = ['password', 'token', 'secret', 'authorization', 'cookie', 'x-api-key'];

        foreach ($data as $key => $value) {
            if (in_array(strtolower((string) $key), $sensitiveKeys, true)) {
                $data[$key] = '**********';

                continue;
            }

            if (is_array($value)) {
                $data[$key] = $this->sanitizeRecursive($value);
            }
        }

        return $data;
    }

    private function truncate(string $value, int $limit): string
    {
        return mb_strlen($value) <= $limit
            ? $value
            : mb_substr($value, 0, $limit - 3) . '...';
    }

    private function formatUser(mixed $user): string
    {
        if ($user === null) {
            return 'Não autenticado';
        }

        $id = method_exists($user, 'getAuthIdentifier')
            ? (string) $user->getAuthIdentifier()
            : 'N/A';

        $email = data_get($user, 'email');

        if (is_string($email) && $email !== '') {
            return "{$id} ({$email})";
        }

        return $id;
    }
}

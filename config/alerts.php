<?php

declare(strict_types = 1);

use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Auth\AuthenticationException;
use Illuminate\Validation\ValidationException;
use Symfony\Component\HttpKernel\Exception\MethodNotAllowedHttpException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

return [
    'discord' => [
        'enabled'            => (bool) env('DISCORD_ALERTS_ENABLED', false),
        'webhook_url'        => env('DISCORD_ALERT_WEBHOOK_URL'),
        'timeout'            => (int) env('DISCORD_ALERT_TIMEOUT', 3),
        'retry_times'        => (int) env('DISCORD_ALERT_RETRY_TIMES', 2),
        'retry_sleep_ms'     => (int) env('DISCORD_ALERT_RETRY_SLEEP_MS', 200),
        'throttle_seconds'   => (int) env('DISCORD_ALERT_THROTTLE_SECONDS', 60),
        'trace_lines'        => (int) env('DISCORD_ALERT_TRACE_LINES', 12),
        'ignored_exceptions' => [
            ValidationException::class,
            AuthenticationException::class,
            AuthorizationException::class,
            NotFoundHttpException::class,
            MethodNotAllowedHttpException::class,
        ],
    ],
];

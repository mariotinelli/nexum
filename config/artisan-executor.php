<?php

declare(strict_types = 1);

return [
    'allowed_ips' => array_values(array_filter(array_map(
        static fn (string $ip): string => trim($ip),
        explode(',', (string) env('ARTISAN_EXECUTOR_ALLOWED_IPS', '127.0.0.1,::1'))
    ))),

    'blocked_commands' => [
        'down',
        'migrate:fresh',
        'migrate:refresh',
        'db:wipe',
    ],

    'allowed_commands' => array_values(array_filter(array_map(
        static fn (string $command): string => trim($command),
        explode(',', (string) env('ARTISAN_EXECUTOR_ALLOWED_COMMANDS', ''))
    ))),

    'allowed_command_prefixes' => array_values(array_filter(array_map(
        static fn (string $command): string => trim($command),
        explode(',', (string) env('ARTISAN_EXECUTOR_ALLOWED_COMMAND_PREFIXES', ''))
    ))),

    'timeout' => (int) env('ARTISAN_EXECUTOR_TIMEOUT', 120),

    'php_binary' => env('ARTISAN_EXECUTOR_PHP_BINARY', ''),
];

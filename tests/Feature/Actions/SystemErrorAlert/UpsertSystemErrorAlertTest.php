<?php

declare(strict_types = 1);

use App\Actions\SystemErrorAlert\UpsertSystemErrorAlert;
use App\Enums\SystemErrorAlertSeverities;
use App\Enums\SystemErrorAlertStatuses;
use App\Models\SystemErrorAlert;

it('creates a new system error alert when fingerprint does not exist', function (): void {
    $attributes = [
        'fingerprint'     => 'abc123',
        'severity'        => SystemErrorAlertSeverities::Critical,
        'environment'     => 'testing',
        'exception_class' => 'RuntimeException',
        'message'         => 'Falha crítica no módulo de faturamento.',
        'file'            => 'app/Services/BillingService.php',
        'line'            => 42,
        'route_name'      => 'dashboard',
        'request_method'  => 'GET',
        'request_url'     => 'http://inova.ai.test/dashboard',
        'request_id'      => 'req-123',
        'user_id'         => null,
        'context'         => ['ip' => '127.0.0.1'],
        'trace'           => '#0 test',
        'occurred_at'     => now(),
    ];

    $systemErrorAlert = app(UpsertSystemErrorAlert::class)->handle($attributes);

    expect($systemErrorAlert->status)->toBe(SystemErrorAlertStatuses::Open)
        ->and($systemErrorAlert->occurrences)->toBe(1)
        ->and($systemErrorAlert->environment)->toBe('testing');

    expect(SystemErrorAlert::query()->whereKey($systemErrorAlert->id)->exists())->toBeTrue();
});

it('updates existing system error alert and increments occurrences', function (): void {
    $alert = SystemErrorAlert::factory()->create([
        'fingerprint' => 'same-fingerprint',
        'environment' => 'testing',
        'occurrences' => 3,
        'status'      => SystemErrorAlertStatuses::Open,
    ]);

    app(UpsertSystemErrorAlert::class)->handle([
        'fingerprint'     => 'same-fingerprint',
        'severity'        => SystemErrorAlertSeverities::Emergency,
        'environment'     => 'testing',
        'exception_class' => 'RuntimeException',
        'message'         => 'Novo erro grave.',
        'file'            => 'app/Services/NewService.php',
        'line'            => 99,
        'route_name'      => 'admin.management.settings.index',
        'request_method'  => 'POST',
        'request_url'     => 'http://inova.ai.test/admin/gestao/configuracoes',
        'request_id'      => 'req-999',
        'user_id'         => null,
        'context'         => ['payload' => 'x'],
        'trace'           => '#0 updated',
        'occurred_at'     => now(),
    ]);

    $alert->refresh();

    expect($alert->occurrences)->toBe(4)
        ->and($alert->severity)->toBe(SystemErrorAlertSeverities::Emergency)
        ->and($alert->message)->toBe('Novo erro grave.')
        ->and($alert->route_name)->toBe('admin.management.settings.index');
});

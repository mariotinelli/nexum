<?php

declare(strict_types = 1);

use App\Enums\SystemErrorAlertSeverities;
use App\Enums\SystemErrorAlertStatuses;
use App\Enums\TypeUsers;
use App\Livewire\Admin\Support\SystemErrorAlerts\Index;
use App\Models\SystemErrorAlert;
use App\Models\User;

use function Pest\Laravel\actingAs;

use function Pest\Livewire\livewire;

beforeEach(function (): void {
    /** @var User $supportUser */
    $supportUser = User::factory()->create([
        'type' => TypeUsers::SupportRemSoft,
    ]);

    actingAs($supportUser);
});

it('can access index with permission', function (): void {
    livewire(Index::class)
        ->assertOk();
});

it('forbids access when user type is not support rem soft', function (): void {
    actingAs(User::factory()->admin()->create());

    livewire(Index::class)
        ->assertForbidden();
});

it('filters alerts by status and severity', function (): void {
    SystemErrorAlert::factory()->create([
        'status'   => SystemErrorAlertStatuses::Open,
        'severity' => SystemErrorAlertSeverities::Critical,
    ]);

    SystemErrorAlert::factory()->create([
        'status'   => SystemErrorAlertStatuses::Resolved,
        'severity' => SystemErrorAlertSeverities::Emergency,
    ]);

    livewire(Index::class)
        ->set('filters.status', (string) SystemErrorAlertStatuses::Resolved->value)
        ->set('filters.severity', (string) SystemErrorAlertSeverities::Emergency->value)
        ->assertSet('alerts', function ($paginator): bool {
            expect($paginator->total())->toBe(1)
                ->and($paginator->items()[0]->status)->toBe(SystemErrorAlertStatuses::Resolved)
                ->and($paginator->items()[0]->severity)->toBe(SystemErrorAlertSeverities::Emergency);

            return true;
        });
});

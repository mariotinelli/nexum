<?php

declare(strict_types = 1);

use App\Brain\Support\Actions\ExecuteArtisanCommandAction;
use App\Enums\CommandExecutionStatuses;
use App\Livewire\Admin\Support\ArtisanCommands\Index;
use App\Models\CommandExecution;
use Illuminate\Support\Facades\Queue;

use function Pest\Livewire\livewire;

it('allows only admin users to access the page', function (): void {
    actingAsUser();

    livewire(Index::class)
        ->assertForbidden();

    actingAsAdmin();

    livewire(Index::class)
        ->assertOk();
});

it('queues a command and persists queued execution log', function (): void {
    actingAsAdmin();

    Queue::fake();

    livewire(Index::class)
        ->call('executeCommand', 'php artisan about')
        ->assertHasNoErrors()
        ->assertDispatched('artisan-commands-clear-input');

    expect(CommandExecution::query()->count())->toBe(1)
        ->and(CommandExecution::query()->first()?->status)->toBe(CommandExecutionStatuses::Queued);

    Queue::assertPushed(ExecuteArtisanCommandAction::class);
});

<?php

declare(strict_types = 1);

use App\Enums\CommandExecutionStatuses;
use App\Livewire\Admin\Support\ArtisanCommands\History;
use App\Models\CommandExecution;

use function Pest\Livewire\livewire;

it('filters command history by status', function (): void {
    actingAsAdmin();

    CommandExecution::factory()->create([
        'status' => CommandExecutionStatuses::Success,
    ]);

    CommandExecution::factory()->create([
        'status' => CommandExecutionStatuses::Error,
    ]);

    livewire(History::class)
        ->set('filters.status', (string) CommandExecutionStatuses::Error->value)
        ->assertSet('commandExecutions', function ($paginator): bool {
            expect($paginator->total())->toBe(1)
                ->and($paginator->items()[0]->status)->toBe(CommandExecutionStatuses::Error);

            return true;
        });
});

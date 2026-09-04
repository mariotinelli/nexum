<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Support\ArtisanCommands;

use App\Brain\Support\Actions\ExecuteArtisanCommandAction;
use App\Enums\CommandExecutionStatuses;
use App\Models\CommandExecution;
use App\Traits\Components\WithModal;
use App\Traits\Components\WithTable;
use App\Traits\Components\WithToast;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\View\View;
use Livewire\Attributes\Computed;
use Livewire\Attributes\On;
use Livewire\Component;

class History extends Component
{
    use WithModal;
    use WithTable;
    use WithToast;

    public ?int $selectedExecutionId = null;

    public function mount(): void
    {
        $this->authorize('view-any', CommandExecution::class);

        $this->sortKeyName = 'executed_at';
        $this->perPage     = 15;
        $this->filters     = $this->emptyFilters();
    }

    #[On('artisan-commands::refresh-history')]
    public function refreshHistory(): void
    {
    }

    public function render(): View
    {
        return view('livewire.admin.support.artisan-commands.history');
    }

    public function emptyFilters(): array
    {
        return [
            'status' => '',
        ];
    }

    public function resetFilters(): void
    {
        $this->filters = $this->emptyFilters();
    }

    public function reExecute(int $commandExecutionId): void
    {
        $this->authorize('create', CommandExecution::class);

        $authenticatedUser = user();

        if ($authenticatedUser === null) {
            abort(403);
        }

        $commandExecution = CommandExecution::query()->findOrFail($commandExecutionId);

        $queuedExecution = CommandExecution::query()->create([
            'user_id'           => $authenticatedUser->id,
            'user_name'         => $authenticatedUser->name,
            'ip_address'        => request()->ip(),
            'command'           => $commandExecution->command,
            'command_name'      => $commandExecution->command_name,
            'command_arguments' => [],
            'status'            => CommandExecutionStatuses::Queued,
            'exit_code'         => null,
            'output'            => null,
            'duration_ms'       => 0,
            'executed_at'       => now(),
        ]);

        ExecuteArtisanCommandAction::dispatch([
            'commandExecutionId' => $queuedExecution->id,
        ]);

        $this->toast('Reexecução enviada para a fila.');
    }

    public function openOutput(int $commandExecutionId): void
    {
        $commandExecution = CommandExecution::query()->findOrFail($commandExecutionId);

        $this->authorize('view', $commandExecution);

        $this->selectedExecutionId = $commandExecution->id;
        $this->openModal();
    }

    #[Computed]
    public function commandExecutions(): LengthAwarePaginator
    {
        return CommandExecution::query()
            ->with('user')
            ->when($this->filters['status'] !== '', fn (Builder $query) => $query->where('status', (int) $this->filters['status']))
            ->when($this->search, function (Builder $query): void {
                $search = "%{$this->search}%";

                $query->where(function (Builder $subQuery) use ($search): void {
                    $subQuery->where('command', 'like', $search)
                        ->orWhere('user_name', 'like', $search)
                        ->orWhere('ip_address', 'like', $search);
                });
            })
            ->orderBy($this->sortKeyName, $this->sortDirection)
            ->paginate($this->perPage);
    }

    #[Computed]
    public function selectedExecution(): ?CommandExecution
    {
        if ($this->selectedExecutionId === null) {
            return null;
        }

        return CommandExecution::query()->find($this->selectedExecutionId);
    }

    #[Computed]
    public function statuses(): array
    {
        return CommandExecutionStatuses::options();
    }
}

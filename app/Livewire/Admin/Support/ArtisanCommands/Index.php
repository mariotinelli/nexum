<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Support\ArtisanCommands;

use App\Brain\Support\Actions\ExecuteArtisanCommandAction;
use App\Enums\CommandExecutionStatuses;
use App\Models\CommandExecution;
use App\Traits\Components\WithToast;
use Illuminate\Support\Facades\Artisan;
use Illuminate\View\View;
use Livewire\Attributes\Computed;
use Livewire\Component;

class Index extends Component
{
    use WithToast;

    public function mount(): void
    {
        $this->authorize('view-any', CommandExecution::class);
    }

    public function render(): View
    {
        return view('livewire.admin.support.artisan-commands.index');
    }

    public function executeCommand(string $command): void
    {
        $this->authorize('create', CommandExecution::class);

        $authenticatedUser = user();

        if ($authenticatedUser === null) {
            abort(403);
        }

        if (trim($command) === '') {
            $this->addError('commandInput', 'Informe um comando artisan válido.');

            return;
        }

        $commandExecution = CommandExecution::query()->create([
            'user_id'           => $authenticatedUser->id,
            'user_name'         => $authenticatedUser->name,
            'ip_address'        => request()->ip(),
            'command'           => trim($command),
            'command_name'      => $this->extractCommandName($command),
            'command_arguments' => [],
            'status'            => CommandExecutionStatuses::Queued,
            'exit_code'         => null,
            'output'            => null,
            'duration_ms'       => 0,
            'executed_at'       => now(),
        ]);

        ExecuteArtisanCommandAction::dispatch([
            'commandExecutionId' => $commandExecution->id,
        ]);

        $this->dispatch('artisan-commands::refresh-history');
        $this->dispatch('artisan-commands-clear-input');

        $this->toast('Comando enviado para a fila de execução.');
    }

    #[Computed]
    public function artisanCommands(): array
    {
        return $this->availableCommands();
    }

    #[Computed]
    public function breadcrumb(): array
    {
        return [
            ['label' => 'Suporte'],
            ['label' => 'Comandos'],
        ];
    }

    /**
     * @return array<int, string>
     */
    private function availableCommands(): array
    {
        return collect(Artisan::all())
            ->keys()
            ->filter(static fn (string $command): bool => $command !== '' && !str_starts_with($command, '_'))
            ->sort()
            ->values()
            ->all();
    }

    private function extractCommandName(string $command): string
    {
        $tokens = array_values(array_filter(
            str_getcsv(trim($command), ' ', '"', '\\'),
            static fn (?string $token): bool => $token !== null && $token !== ''
        ));

        if (($tokens[0] ?? null) === 'php') {
            array_shift($tokens);
        }

        if (($tokens[0] ?? null) === 'artisan') {
            array_shift($tokens);
        }

        $commandName = array_shift($tokens);

        if (!is_string($commandName)) {
            return 'unknown';
        }

        return $commandName;
    }
}

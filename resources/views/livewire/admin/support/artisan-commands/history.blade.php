<div class="mt-6">
    <x-ui.table :records="$this->commandExecutions">
        <x-slot name="filtersDropdown">
            <x-ui.input.select
                name="filters.status"
                label="Status"
                :options="$this->statuses"
                wire:model.blur="filters.status"
            />
        </x-slot>

        <x-slot name="header">
            <x-ui.table.th name="command">Comando</x-ui.table.th>
            <x-ui.table.th name="status">Status</x-ui.table.th>
            <x-ui.table.th name="user_name">Usuário</x-ui.table.th>
            <x-ui.table.th name="ip_address">IP</x-ui.table.th>
            <x-ui.table.th name="duration_ms">Duração</x-ui.table.th>
            <x-ui.table.th name="executed_at">Executado em</x-ui.table.th>
            <x-ui.table.th></x-ui.table.th>
        </x-slot>

        <x-slot name="body">
            @forelse ($this->commandExecutions as $execution)
                <x-ui.table.tr wire:key="command-execution-{{ $execution->id }}">
                    <x-ui.table.td>
                        <button
                            type="button"
                            id="open-command-output-{{ $execution->id }}"
                            wire:click="openOutput({{ $execution->id }})"
                            class="text-info max-w-104 truncate text-left text-sm font-medium hover:underline"
                            title="{{ $execution->command }}"
                        >
                            {{ $execution->command }}
                        </button>
                    </x-ui.table.td>

                    <x-ui.table.td>
                        <x-ui.badge :color="$execution->status->color()">
                            {{ $execution->status->label() }}
                        </x-ui.badge>
                    </x-ui.table.td>

                    <x-ui.table.td>
                        <div class="flex flex-col">
                            <span>{{ $execution->user_name }}</span>
                            <span class="text-xs text-gray-500">#{{ $execution->user_id ?? 'N/A' }}</span>
                        </div>
                    </x-ui.table.td>

                    <x-ui.table.td>{{ $execution->ip_address ?? 'N/A' }}</x-ui.table.td>
                    <x-ui.table.td>{{ number_format($execution->duration_ms, 0, ',', '.') }} ms</x-ui.table.td>
                    <x-ui.table.td>{{ $execution->executed_at->format('d/m/Y H:i:s') }}</x-ui.table.td>

                    <x-ui.table.td>
                        <div class="flex items-center justify-end gap-1">
                            <x-ui.button
                                id="show-output-button-{{ $execution->id }}"
                                class="tooltip table-action"
                                data-tip="Ver console"
                                ghost
                                xs
                                wire:click="openOutput({{ $execution->id }})"
                                :with-loading="false"
                            >
                                <x-icons.command-line class="text-info size-5!" />
                            </x-ui.button>

                            <x-ui.button
                                id="rerun-command-button-{{ $execution->id }}"
                                class="tooltip table-action"
                                data-tip="Reexecutar"
                                ghost
                                xs
                                wire:click="reExecute({{ $execution->id }})"
                                loading="reExecute({{ $execution->id }})"
                                :with-loading="false"
                            >
                                <x-icons.arrow-path class="text-success size-5!" />
                            </x-ui.button>
                        </div>
                    </x-ui.table.td>
                </x-ui.table.tr>
            @empty
                <x-ui.table.tr>
                    <x-ui.table.td colspan="7" class="text-center !text-gray-500">
                        Nenhum comando executado até o momento.
                    </x-ui.table.td>
                </x-ui.table.tr>
            @endforelse
        </x-slot>
    </x-ui.table>

    <x-ui.modal id="artisan-command-output-modal" xl2 divided scrollable>
        <x-slot name="title">Saída do comando</x-slot>

        <x-slot name="description">
            {{ $this->selectedExecution?->command ?? 'Selecione um registro para visualizar o console.' }}
        </x-slot>

        <div class="space-y-4">
            @if ($this->selectedExecution)
                <div class="grid gap-2 text-sm text-gray-600 md:grid-cols-2">
                    <p><strong>Status:</strong> {{ $this->selectedExecution->status->label() }}</p>
                    <p>
                        <strong>Duração:</strong>
                        {{ number_format($this->selectedExecution->duration_ms, 0, ',', '.') }} ms
                    </p>
                    <p><strong>Usuário:</strong> {{ $this->selectedExecution->user_name }}</p>
                    <p><strong>IP:</strong> {{ $this->selectedExecution->ip_address ?? 'N/A' }}</p>
                </div>

                <div class="overflow-auto rounded-lg border border-gray-900 bg-gray-950 p-4 text-xs leading-5 text-green-300">
                    <pre class="font-mono whitespace-pre-wrap">{{ $this->selectedExecution->output ?: 'Sem saída registrada.' }}</pre>
                </div>
            @else
                <p class="text-sm text-gray-500">Nenhum comando selecionado.</p>
            @endif
        </div>

        <x-slot name="footer">
            <div class="flex w-full items-center justify-end gap-2 bg-gray-100 p-3">
                <x-ui.button cancel-button sm wire:click="closeModal">Fechar</x-ui.button>

                @if ($this->selectedExecution)
                    <x-ui.button
                        sm
                        primary
                        icon="arrow-path"
                        wire:click="reExecute({{ $this->selectedExecution->id }})"
                    >
                        Reexecutar
                    </x-ui.button>
                @endif
            </div>
        </x-slot>
    </x-ui.modal>
</div>

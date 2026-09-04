<x-ui.page
    title="Alertas de Erro"
    description="Central de monitoramento de exceções críticas do sistema."
    :breadcrumb="$this->breadcrumb"
>
    <x-ui.table :records="$this->alerts">
        <x-slot name="filtersDropdown">
            <x-ui.input.select
                name="filters.status"
                label="Status"
                :options="$this->statuses"
                wire:model.blur="filters.status"
            />

            <x-ui.input.select
                name="filters.severity"
                label="Severidade"
                :options="$this->severities"
                wire:model.blur="filters.severity"
            />

            <x-ui.input.select
                name="filters.environment"
                label="Ambiente"
                :options="$this->environmentOptions"
                wire:model.blur="filters.environment"
            />
        </x-slot>

        <x-slot name="header">
            <x-ui.table.th name="last_seen_at">Última ocorrência</x-ui.table.th>
            <x-ui.table.th name="exception_class">Exceção</x-ui.table.th>
            <x-ui.table.th name="environment">Ambiente</x-ui.table.th>
            <x-ui.table.th name="severity">Severidade</x-ui.table.th>
            <x-ui.table.th name="status">Status</x-ui.table.th>
            <x-ui.table.th name="occurrences">Ocorrências</x-ui.table.th>
            <x-ui.table.th name="request_method">Requisição</x-ui.table.th>
            <x-ui.table.th></x-ui.table.th>
        </x-slot>

        <x-slot name="body">
            @forelse ($this->alerts as $alert)
                <x-ui.table.tr>
                    <x-ui.table.td>{{ $alert->last_seen_at?->format('d/m/Y H:i:s') }}</x-ui.table.td>
                    <x-ui.table.td>
                        <div class="font-medium">{{ $alert->exception_class }}</div>
                        <div class="max-w-80 truncate text-xs text-gray-600">{{ $alert->message }}</div>
                    </x-ui.table.td>
                    <x-ui.table.td>{{ $alert->environment }}</x-ui.table.td>
                    <x-ui.table.td>
                        <x-ui.badge :color="$alert->severity->color()">{{ $alert->severity->label() }}</x-ui.badge>
                    </x-ui.table.td>
                    <x-ui.table.td>
                        <x-ui.badge :color="$alert->status->color()">{{ $alert->status->label() }}</x-ui.badge>
                    </x-ui.table.td>
                    <x-ui.table.td>{{ $alert->occurrences }}</x-ui.table.td>
                    <x-ui.table.td>
                        <div
                            class="max-w-72 truncate text-xs text-gray-700"
                            title="{{ $alert->request_method }} {{ parse_url((string) $alert->request_url, PHP_URL_PATH) ?? 'N/A' }}"
                        >
                            {{ $alert->request_method }} {{ parse_url((string) $alert->request_url, PHP_URL_PATH) ?? 'N/A' }}
                        </div>
                    </x-ui.table.td>
                    <x-ui.table.td>
                        <x-ui.button
                            id="show-system-error-alert-{{ $alert->id }}"
                            class="tooltip table-action"
                            data-tip="Visualizar"
                            ghost
                            xs
                            href="{{ route('admin.support.system-error-alerts.show', $alert) }}"
                        >
                            <x-icons.eye class="text-info !size-5" />
                        </x-ui.button>
                    </x-ui.table.td>
                </x-ui.table.tr>
            @empty
                <x-ui.table.tr>
                    <x-ui.table.td colspan="8" class="text-center !text-gray-500">
                        Nenhum alerta encontrado
                    </x-ui.table.td>
                </x-ui.table.tr>
            @endforelse
        </x-slot>
    </x-ui.table>
</x-ui.page>

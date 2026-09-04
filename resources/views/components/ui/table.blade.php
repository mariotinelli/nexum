@use('Illuminate\Pagination\AbstractPaginator')

@props([
    'records',
    'search'            => true,
    'pagination'        => true,
    'header'            => null,
    'body'              => null,
    'filtersHeader'     => null,
    'filtersDropdown'   => null,
    'tableHeader'       => null,
    'searchInput'       => null,
    'toggleOnlyTrashed' => false,
])

@php
    $activeFilters = 0;
    $searchId      = 'table-search-' . str()->ulid();

    $filters = $this->filters ?? [];

    foreach ($filters as $filter) {
        if (is_array($filter)) {
            $activeFilters += count($filter) === 0 ? 0 : 1;

            continue;
        }

        $activeFilters += empty($filter) ? 0 : 1;
    }
@endphp

<div {{ $attributes->merge(['class' => 'mx-auto rounded-lg w-full bg-white border border-gray-300']) }}>
    @if ($filtersHeader || $search || $filtersDropdown)
        <div @class([
            'p-4 flex items-end gap-3 justify-end',
            'px-8!' => $filtersDropdown,
        ])>
            @if ($filtersHeader)
                <div class="flex h-full items-end">{{ $filtersHeader }}</div>
            @endif

            @if ($search || $filtersDropdown || $toggleOnlyTrashed)
                <div class="flex items-center gap-3">
                    @if ($toggleOnlyTrashed)
                        <x-ui.input.toggle
                            inline
                            label-right
                            label="Mostrar apenas desativados"
                            wire:model.live="toggleOnlyTrashed"
                        />
                    @endif

                    @if ($search)
                        @if ($searchInput)
                            {{ $searchInput }}
                        @else
                            <label for="{{ $searchId }}" class="sr-only">Buscar itens na tabela</label>
                            <x-ui.input
                                id="{{ $searchId }}"
                                type="search"
                                placeholder="Buscar itens na tabela"
                                wire:model.live.debounce.400ms="search"
                                class="min-w-64"
                                aria-label="Buscar itens na tabela"
                            >
                                <x-slot name="prefix">
                                    <x-icons.magnifying-glass class="size-6" aria-hidden="true" />
                                </x-slot>
                            </x-ui.input>
                        @endif
                    @endif

                    @if ($filtersDropdown)
                        <x-ui.dropdown bottom end lg>
                            <x-slot name="trigger">
                                <button
                                    id="open-filters"
                                    type="button"
                                    class="relative"
                                    aria-label="Abrir filtros, {{ $activeFilters }} filtros ativos"
                                >
                                    <x-ui.badge primary circle sm class="absolute -top-3 -right-4">
                                        {{ $activeFilters }}
                                    </x-ui.badge>

                                    <x-icons.funnel class="h-5 w-5 cursor-pointer text-gray-400" aria-hidden="true" />
                                </button>
                            </x-slot>

                            <span class="sr-only" aria-live="polite">{{ $activeFilters }} filtros ativos</span>

                            <div class="space-y-4 p-6">
                                <div class="flex items-center justify-between gap-4">
                                    <x-ui.title sm>Filtros</x-ui.title>

                                    <button
                                        id="reset-filters"
                                        type="button"
                                        wire:click="resetFilters"
                                        class="hover:text-decoration-line: text-red-600 underline hover:cursor-pointer"
                                        aria-label="Limpar todos os filtros ativos"
                                    >
                                        Limpar
                                    </button>
                                </div>

                                {{ $filtersDropdown }}
                            </div>
                        </x-ui.dropdown>
                    @endif
                </div>
            @endif
        </div>
    @endif

    <div @class([
        '-mx-4 sm:mx-0 overflow-x-auto border-b border-gray-300',
        'sm:rounded-t-lg'                          => !$search && !$filtersHeader && !$filtersDropdown,
        'border-t'                                 => $search || $filtersHeader || $filtersDropdown,
        'max-h-[40rem] border-b-0 sm:rounded-b-lg' => !$pagination || !$records instanceof AbstractPaginator,
    ])>
        <table
            @class([
                'min-w-full divide-y divide-gray-300 sm:rounded-lg',
                'max-h-[40rem] overflow-auto' => !$pagination || !$records instanceof AbstractPaginator,
            ])
            aria-label="Tabela de resultados"
        >
            <thead>
                @if ($tableHeader)
                    <tr class="bg-white">
                        {{ $tableHeader }}
                    </tr>
                @endif

                <tr class="bg-gray-100">
                    {{ $header }}
                </tr>
            </thead>

            <tbody class="divide-y divide-gray-200 bg-white">
                {{ $body }}
            </tbody>
        </table>
    </div>

    @if ($pagination && $records instanceof AbstractPaginator)
        <div class="flex items-center justify-between px-4 pt-2 pb-4">
            <nav aria-label="Paginação" class="w-full">
                {{ $records->links('components.ui.pagination', ['recordCount' => 'full', 'perPageValues' => $this->perPageValues]) }}
            </nav>
        </div>
    @endif
</div>

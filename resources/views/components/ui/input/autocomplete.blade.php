@props([
    'name',
    'route',
    'withInfinityScroll' => true,
    'id'                 => null,
    'label'              => null,
    'wire'               => null,
    'labeless'           => false,
    'showError'          => true,
    'helperText'         => null,
    'hint'               => null,
    'prefix'             => null,
    'suffix'             => null,
    'params'             => [],
])

@php
    use Illuminate\Support\Facades\View;

    $name ??= $attributes->wire('model')->value();
    $id        = $id ?? $name;
    $wireModel = $attributes->whereStartsWith('wire:model')->first();

    $isLive = !isset($attributes->getAttributes()['wire:model']);
@endphp

<div
    x-data="autocomplete({
    search: null,
    value: @entangle($wireModel),
    wireModel: '{{ $wireModel }}',
    open: false,
    withInfinityScroll: '{{ $withInfinityScroll ? 1 : 0 }}',
    name: '{{ $name }}',
    route: '{{ $route }}',
    suffix: {{ $suffix ? 1 : 0 }},
    prefix: {{ $prefix ? 1 : 0 }},
    isLive: {{ $isLive ? 1 : 0 }},
})"
    x-init="init(@this, $el)"
    class="w-full"
>
    <div class="relative">
        <x-ui.input
            {{ $attributes->whereDoesntStartWith('wire:model') }}
            :name="$attributes->wire('model')->value()"
            x-ref="autocomplete"
            x-model="value"
            x-on:focus="onFocus"
            x-on:click.away="close"
        >
            <x-slot name="prefix">
                <x-icons.magnifying-glass class="size-6" />
            </x-slot>
        </x-ui.input>

        <div
            x-show="open"
            x-transition:leave="transition ease-in duration-100"
            x-transition:leave-start="opacity-100"
            x-transition:leave-end="opacity-0"
            class="ring-opacity-5 absolute z-10 mt-1 max-h-56 w-full overflow-auto rounded-md bg-white text-base shadow-lg ring-1 ring-gray-200 focus:outline-hidden sm:text-sm"
            tabindex="-1"
            style="display: none"
            x-ref="selectBox"
        >
            <ul
                class="relative max-h-56 p-1 focus:outline-hidden"
                role="listbox"
                x-max="1"
                x-ref="ul"
                aria-labelledby="listbox-label"
                x-bind:aria-activedescendant="activeDescendant"
            >
                <template x-if="loading">
                    <li
                        class="relative flex items-center justify-center gap-1 py-2 pr-4 pl-8 text-sm text-gray-900 select-none"
                        role="option"
                    >
                        <x-icons.loading class="h-5 w-5 animate-spin text-gray-400" />
                        <span>Carregando</span>
                    </li>
                </template>

                <template x-if="items.length === 0 && ! loading && value.length > 0">
                    <li class="relative py-2 pr-4 pl-8 text-sm text-gray-900 select-none" role="option">
                        {{ $emptyLabel ?? 'Nenhum resultado encontrado' }}
                    </li>
                </template>

                <template x-if="value.length === 0 && items.length === 0 && ! loading">
                    <li class="relative py-2 pr-4 pl-8 text-sm text-gray-900 select-none" role="option">
                        Digite ao menos 2 caracteres para buscar
                    </li>
                </template>

                <template x-if="items.length > 0 && ! loading">
                    <template x-for="(item, index) in items" :key="index">
                        <li
                            class="hover:bg-primary relative rounded-md py-2 pr-4 pl-8 text-sm text-gray-900 select-none hover:cursor-pointer hover:text-white"
                            role="option"
                            x-on:click="choose(index)"
                            x-bind:id="`${name}::${item.id}}`"
                        >
                            <span class="block truncate p-0! font-normal" x-text="item.name"></span>
                        </li>
                    </template>
                </template>
            </ul>
        </div>
    </div>
</div>

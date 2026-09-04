@props([
    'name',
    'route',
    'withInfinityScroll' => true,
    'initialValue'       => [],
    'withSearch'         => true,
    'id'                 => null,
    'label'              => null,
    'wire'               => null,
    'labeless'           => false,
    'defaultOptionLabel' => 'Selecione uma ou mais opções',
    'showError'          => true,
    'helperText'         => null,
    'hint'               => null,
    'prefix'             => null,
    'suffix'             => null,
    'selectedColumn'     => 'id',
    'parentClass'        => null,
])

@php
    $name ??= $attributes->wire('model')->value();
    $id        = $id ?? $name;
    $wireModel = $attributes->whereStartsWith('wire:model')->first();

    $isLive = !isset($attributes->getAttributes()['wire:model']);
@endphp

<div
    x-data="multiSelectSearch({
    search: null,
    initialValue: {{ json_encode($initialValue) }},
    value: @entangle($wireModel).live,
    wireModel: '{{ $wireModel }}',
    open: false,
    withInfinityScroll: '{{ $withInfinityScroll ? 1 : 0 }}',
    name: '{{ $name }}',
    route: '{{ $route }}',
    withSearch: '{{ $withSearch ? 1 : 0 }}',
    defaultOptionLabel: {{ json_encode($defaultOptionLabel) }},
    suffix: {{ $suffix ? 1 : 0 }},
    prefix: {{ $prefix ? 1 : 0 }},
    selectedColumn: '{{ $selectedColumn }}',
    isLive: {{ $isLive ? 1 : 0 }},
})"
    x-init="init(@this, $el)"
    class="w-full {{ $parentClass }}"
>
    @unless ($labeless)
        <div class="flex items-center justify-between">
            <x-ui.input.label
                :name="$name"
                id="listbox-label"
                x-on:click="$refs.button.focus()"
                :required="$attributes->get('required')"
            >
                {{ $label }}
            </x-ui.input.label>

            @if ($hint)
                <span class="text-sm text-gray-500">{{ $hint }}</span>
            @endif
        </div>
    @endunless

    <div class="relative mt-1">
        <div
            @class([
                'flex items-center cursor-default min-h-10! rounded-lg',
                'border border-gray-950/10 focus-within:ring-2 focus-within:ring-primary overflow-hidden ' => $prefix || $suffix,
                'border-error!'                                                                            => $errors->has($wireModel),
                'bg-gray-100'                                                                              => $attributes->get('disabled'),
            ])
            x-bind:class="{
                'ring-1! ring-primary! border-primary!': open && (suffix || prefix),
            }"
        >
            @if ($prefix)
                <div
                    wire:loading.class="bg-gray-100"
                    class="flex min-w-10 items-center justify-center border-r border-r-gray-950/10 p-0! py-1.5! text-gray-500 hover:cursor-default"
                    x-bind:class="{
                        'py-[0.3rem]!': ! selectedItems.length,
                        'py-1.5!': selectedItems.length,
                    }"
                >
                    {{ $prefix }}
                </div>
            @endif

            <button
                id="{{ $id }}"
                @class([
                    'relative w-full bg-white rounded-lg pl-3 pr-10 py-2 text-left focus:outline-hidden sm:text-sm disabled:bg-gray-100',
                    'border-error! ring-0!'                                                           => $errors->has($wireModel),
                    'border border-gray-950/10 focus:ring-1 focus:ring-primary focus:border-primary ' => !$suffix && !$prefix,
                ])
                type="button"
                x-on:click="openList()"
                x-on:keydown.arrow-down.stop.prevent="open ? onArrowDown() : openList()"
                x-on:keydown.arrow-up.stop.prevent="open ? onArrowUp() : openList()"
                x-on:keydown.space.stop.prevent="open ? onOptionSelect() : openList()"
                x-on:keydown.enter.stop.prevent="open ? onOptionSelect() : openList()"
                x-on:keydown.escape="onEscape()"
                x-ref="button"
                :aria-expanded="open"
                @disabled($attributes->get('disabled'))
                aria-labelledby="listbox-label"
                x-bind:class="{
                    'ring-1! ring-primary! border-primary!': open && ! suffix && ! prefix,
                    'py-1.5!': selectedItems.length,
                }"
                wire:loading.attr="disabled"
            >
                <span class="block truncate">
                    <template x-if="selectedItems.length">
                        <div class="flex flex-wrap gap-2">
                            <template x-for="(item, index) in selected" :key="index">
                                <x-ui.badge xs primary right-icon>
                                    <x-slot name="icon">
                                        <x-icons.x-mark
                                            @class([
                                                'h-4 w-4 text-primary',
                                                'cursor-pointer hover:text-primary/50' => !$attributes->get('disabled'),
                                                'pointer-events-none'                  => $attributes->get('disabled'),
                                            ])
                                            @click.stop="remove(item.id)"
                                        />
                                    </x-slot>

                                    <span x-text="item.name"></span>
                                </x-ui.badge>
                            </template>
                        </div>
                    </template>
                    <template x-if="! selectedItems.length">
                        <span class="text-gray-500" x-text="defaultOptionLabel"></span>
                    </template>
                </span>

                <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                    <template x-if="loading">
                        <x-icons.loading class="h-5 w-5 animate-spin text-gray-400" />
                    </template>
                    <template x-if="! loading">
                        <x-icons.selector class="h-5 w-5 text-gray-400" />
                    </template>
                </span>
            </button>

            @if ($suffix)
                <div
                    wire:loading.class="bg-gray-100"
                    class="flex min-w-10 items-center justify-center border-l border-gray-950/10 p-0! py-1.5! text-gray-500 hover:cursor-default"
                >
                    {{ $suffix }}
                </div>
            @endif
        </div>

        <div
            x-show="open"
            x-transition:leave="transition ease-in duration-100"
            x-transition:leave-start="opacity-100"
            x-transition:leave-end="opacity-0"
            x-on:keydown.escape="onEscape()"
            x-on:click.away="open = false"
            class="ring-opacity-5 absolute z-10 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-gray-200 focus:outline-hidden sm:text-sm"
            x-bind:class="{
                'mt-1': ! dropdownUp,
                'mb-1 bottom-full': dropdownUp,
            }"
            tabindex="-1"
            style="display: none"
            x-ref="multiSelectSearchBox"
            x-on:scroll="infinityScroll()"
        >
            @if ($withSearch)
                <div class="relative flex cursor-default items-center gap-1 shadow-xs">
                    <x-icons.search-circle class="h-7 w-7 pb-0.5 pl-2 text-gray-500" />
                    <input
                        x-ref="search"
                        type="text"
                        x-model="search"
                        x-on:input.debounce="doSearch()"
                        x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
                        x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
                        x-on:keydown.enter.stop.prevent="onOptionSelect()"
                        x-on:keydown.escape="onEscape()"
                        class="w-full border-0 py-2 focus:ring-0 focus-visible:outline-hidden"
                        placeholder="Buscar..."
                    />
                </div>
            @endif

            <ul
                class="relative max-h-60 p-1 focus:outline-hidden"
                role="listbox"
                x-max="1"
                x-ref="ul"
                tabindex="0"
                x-on:keydown.enter.stop.prevent="onOptionSelect()"
                x-on:keydown.space.stop.prevent="onOptionSelect()"
                x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
                x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
                aria-labelledby="listbox-label"
                x-bind:aria-activedescendant="activeDescendant"
            >
                <template x-if="filteredItems.length === 0">
                    <li class="relative pt-3 pr-4 pb-2 pl-8 text-sm text-gray-900 select-none" role="option">
                        Nenhum resultado encontrado
                    </li>
                </template>

                <template x-if="filteredItems.length > 0">
                    <template x-for="(item, index) in filteredItems" :key="index">
                        <li
                            class="relative rounded-md py-2 pr-4 pl-8 text-sm text-gray-900 select-none hover:cursor-pointer"
                            role="option"
                            x-on:click="choose(index)"
                            x-on:mouseenter="activeIndex = index"
                            x-on:mouseleave="activeIndex = null"
                            x-bind:class="{
                                'bg-primary text-white': activeIndex === index,
                                'hover:bg-primary hover:text-white': activeIndex !== index,
                            }"
                        >
                            <span class="block truncate p-0! font-normal" x-text="item.name"> </span>
                        </li>
                    </template>
                </template>
            </ul>
        </div>
    </div>

    <div class="mt-1.5 flex flex-col gap-1">
        @if ($showError)
            @error($wireModel)
                <x-ui.input.error :message="$message" />
            @enderror
        @endif

        @if ($helperText)
            <span class="text-sm break-words text-gray-500">{{ $helperText }}</span>
        @endif
    </div>
</div>

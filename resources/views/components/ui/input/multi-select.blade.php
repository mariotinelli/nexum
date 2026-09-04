@props([
    'name',
    'initialValue'       => [],
    'id'                 => null,
    'label'              => null,
    'options'            => [],
    'labeless'           => false,
    'showError'          => true,
    'defaultOptionLabel' => 'Selecione uma ou mais opções',
    'helperText'         => null,
    'hint'               => null,
    'prefix'             => null,
    'suffix'             => null,
    'clearable'          => true,
])

@php
    $name ??= $attributes->wire('model')->value();
    $id        = $id ?? $name;
    $uid       = (string) str()->ulid();
    $labelId   = "{$id}-label-{$uid}";
    $listboxId = "{$id}-listbox-{$uid}";
    $errorId   = "{$id}-error-{$uid}";
    $wireModel = $attributes->whereStartsWith('wire:model')->first();

    $isLive = !isset($attributes->getAttributes()['wire:model']);
@endphp

<div
    x-data="multiSelect({
    initialValue: {{ Js::from($initialValue) }},
    value: @entangle($wireModel).live,
    wireModel: '{{ $wireModel }}',
    open: false,
    name: '{{ $name }}',
    items: {{ Js::from($options) }},
    defaultOptionLabel: {{ Js::from($defaultOptionLabel) }},
    suffix: {{ $suffix ? 1 : 0 }},
    prefix: {{ $prefix ? 1 : 0 }},
    clearable: {{ $clearable ? 1 : 0 }},
    isLive: {{ $isLive ? 1 : 0 }},
})"
    x-init="init(@this, $el)"
    x-on:keydown.escape.window.stop.prevent="open ? onEscape() : null"
    x-on:keydown.arrow-down.window.stop.prevent="open ? onArrowDown() : null"
    x-on:keydown.arrow-up.window.stop.prevent="open ? onArrowUp() : null"
    x-on:keydown.enter.window.stop.prevent="open ? onOptionSelect() : null"
    x-on:keydown.space.window.stop.prevent="open ? onOptionSelect() : null"
    class="w-full"
>
    @unless ($labeless)
        <div class="flex items-center justify-between">
            <x-ui.input.label
                :name="$name"
                :id="$id"
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

    <span id="{{ $labelId }}" class="sr-only">{{ $label ?: $defaultOptionLabel }}</span>

    <div class="relative mt-1">
        <div
            @class([
                'flex items-center cursor-default min-h-10! rounded-lg ',
                'border border-gray-950/10 focus-within:ring-2 focus-within:ring-primary overflow-hidden ' => $prefix || $suffix,
                'border-error!'                                                                            => $errors->has($wireModel),
                'bg-gray-100'                                                                              => $attributes->get('disabled'),
            ])
            x-bind:class="{
                'ring-1! ring-primary! border-primary!': open && (suffix || prefix),
            }"
        >
            @if ($prefix)
                <div class="h-full" wire:loading.class="bg-gray-100">
                    <div
                        class="flex min-w-10 items-center justify-center border-r border-r-gray-950/10 text-gray-500 hover:cursor-default"
                        x-bind:class="{
                            'py-[0.3rem]!': ! selectedItems.length,
                            'py-1.5!': selectedItems.length,
                        }"
                    >
                        {{ $prefix }}
                    </div>
                </div>
            @endif

            <button
                id="{{ $id }}"
                @class([
                    'relative w-full bg-white rounded-lg pl-3 pr-10 py-2 text-left focus:outline-hidden sm:text-sm min-h-10! disabled:bg-gray-100',
                    'border-error! ring-0!'                                                           => $errors->has($wireModel),
                    'border border-gray-950/10 focus:ring-1 focus:ring-primary focus:border-primary ' => !$suffix && !$prefix,
                ])
                type="button"
                x-on:click="onButtonClick()"
                x-on:keydown.arrow-down.stop.prevent="open ? onArrowDown() : onButtonClick()"
                x-on:keydown.arrow-up.stop.prevent="open ? onArrowUp() : onButtonClick()"
                x-on:keydown.space.stop.prevent="open ? onOptionSelect() : onButtonClick()"
                x-on:keydown.enter.stop.prevent="open ? onOptionSelect() : onButtonClick()"
                x-on:keydown.escape="onEscape()"
                x-ref="button"
                @disabled($attributes->get('disabled'))
                role="combobox"
                aria-haspopup="listbox"
                :aria-expanded="open"
                aria-controls="{{ $listboxId }}"
                aria-required="{{ $attributes->get('required') ? 'true' : 'false' }}"
                aria-invalid="{{ $errors->has($wireModel) ? 'true' : 'false' }}"
                @if ($showError && $errors->has($wireModel)) aria-describedby="{{ $errorId }}" @endif
                x-bind:class="{
                    'ring-1! ring-primary! border-primary!': open && ! suffix && ! prefix,
                    'py-1.5!': selectedItems.length,
                }"
                wire:loading.attr="disabled"
            >
                <span class="block truncate">
                    <template x-if="selectedItems.length">
                        <ul role="list" class="flex flex-wrap items-center gap-2">
                            <template x-for="(item, index) in selected">
                                <li>
                                    <x-ui.badge xs primary right-icon>
                                        <x-slot name="icon">
                                            <button
                                                type="button"
                                                tabindex="-1"
                                                x-bind:aria-label="`Remover ${item.name}`"
                                                @click.stop="remove(item.id)"
                                                @disabled($attributes->get('disabled'))
                                            >
                                                <x-icons.x-mark @class([
                                                    'h-4 w-4 text-primary',
                                                    'cursor-pointer hover:text-primary/50' => !$attributes->get('disabled'),
                                                    'pointer-events-none'                  => $attributes->get('disabled'),
                                                ]) />
                                            </button>
                                        </x-slot>

                                        <span x-text="item.name"></span>
                                    </x-ui.badge>
                                </li>
                            </template>
                        </ul>
                    </template>

                    <template x-if="! selectedItems.length">
                        <span x-text="defaultOptionLabel" class="text-gray-500"></span>
                    </template>
                </span>

                <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                    <x-icons.selector class="h-5 w-5 text-gray-400" />
                </span>
            </button>

            <span class="sr-only" aria-live="polite">
                <span x-text="`${selectedItems.length} itens selecionados`"></span> itens selecionados
            </span>

            @if ($suffix)
                <div
                    wire:loading.class="bg-gray-100"
                    class="flex min-w-10 items-center justify-center border-l border-gray-950/10 p-0! text-gray-500 hover:cursor-default"
                    x-bind:class="{
                        'py-[0.3rem]!': ! selectedItems.length,
                        'py-1.5!': selectedItems.length,
                    }"
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
            class="ring-opacity-5 absolute z-10 max-h-56 w-full overflow-auto rounded-md bg-white text-base shadow-lg ring-1 ring-gray-200 focus:outline-hidden sm:text-sm"
            x-bind:class="{
                'mt-1': ! dropdownUp,
                'mb-1 bottom-full': dropdownUp,
            }"
            tabindex="-1"
            style="display: none"
            x-ref="selectMultipleBox"
        >
            <ul
                class="relative max-h-56 focus:outline-hidden"
                id="{{ $listboxId }}"
                role="listbox"
                aria-multiselectable="true"
                x-max="1"
                x-ref="ul"
                tabindex="0"
                x-on:keydown.enter.stop.prevent="onOptionSelect()"
                x-on:keydown.space.stop.prevent="onOptionSelect()"
                x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
                x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
                aria-labelledby="{{ $labelId }}"
                x-bind:aria-activedescendant="activeDescendant"
            >
                <template x-if="filteredItems.length === 0">
                    <li class="relative py-2 pr-4 pl-8 text-sm text-gray-900 select-none" role="option">
                        Nenhum resultado encontrado
                    </li>
                </template>

                <template x-if="filteredItems.length > 0">
                    <template x-for="(item, index) in filteredItems" :key="index">
                        <li
                            class="relative rounded-md py-2 pr-4 pl-8 text-sm text-gray-900 select-none hover:cursor-pointer"
                            role="option"
                            x-bind:aria-selected="isSelected(index)"
                            x-on:click="choose(index)"
                            x-bind:id="`${name}::${item.id}`"
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

    @if ($showError)
        @error($wireModel)
            <x-ui.input.error :id="$errorId" :message="$message" />
        @enderror
    @endif

    @if ($helperText)
        <span class="text-sm break-words text-gray-500">{{ $helperText }}</span>
    @endif
</div>

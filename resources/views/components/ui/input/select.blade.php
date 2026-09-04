@props([
    'name',
    'initialValue'       => null,
    'id'                 => null,
    'label'              => null,
    'options'            => [],
    'labeless'           => false,
    'showError'          => true,
    'defaultOptionLabel' => 'Selecione uma opção',
    'helperText'         => null,
    'hint'               => null,
    'prefix'             => null,
    'suffix'             => null,
    'clearable'          => true,
    'parentClass'        => null,
    'emptyLabel'         => null,
])

@php
    $name ??= $attributes->wire('model')->value();
    $id        = $id ?? $name;
    $uid       = (string) str()->ulid();
    $labelId   = "{$id}-label-{$uid}";
    $listboxId = "{$id}-listbox-{$uid}";

    $wireModel = $attributes->whereStartsWith('wire:model')->first();

    $isLive = !isset($attributes->getAttributes()['wire:model']);
@endphp

<div
    x-data="select({
    initialValue: '{{ $initialValue }}',
    value: @entangle($wireModel).live,
    wireModel: '{{ $wireModel }}',
    open: false,
    name: '{{ $name }}',
    items: {{ Js::from($options) }},
    defaultOptionLabel: '{{ $defaultOptionLabel }}',
    suffix: {{ $suffix ? 1 : 0 }},
    prefix: {{ $prefix ? 1 : 0 }},
    clearable: {{ $clearable ? 1 : 0 }},
    isLive: {{ $isLive ? 1 : 0 }},
})"
    x-init="init(@this, $el)"
    class="w-full {{ $parentClass }}"
>
    @unless ($labeless)
        <div class="flex items-center justify-between">
            <x-ui.input.label
                :name="$name"
                :id="$labelId"
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

    @if ($labeless)
        <span id="{{ $labelId }}" class="sr-only">{{ $label ?: $defaultOptionLabel }}</span>
    @endif

    <div class="relative mt-1">
        <div
            @class([
                'flex items-center cursor-default h-10! rounded-lg',
                'border border-gray-950/10 focus-within:ring-2 focus-within:ring-primary overflow-hidden ' => $prefix || $suffix,
                'border-error!'                                                                            => $errors->has($wireModel),
                'bg-gray-100'                                                                              => $attributes->get('disabled'),
            ])
            x-bind:class="{
                'ring-1! ring-primary! border-primary!': open && (prefix || suffix),
            }"
        >
            @if ($prefix)
                <div
                    wire:loading.class="bg-gray-100"
                    class="flex min-w-10 items-center justify-center border-r border-r-gray-950/10 !p-0 !py-1.5 text-gray-500 hover:cursor-default"
                >
                    {{ $prefix }}
                </div>
            @endif

            <button
                id="{{ $id }}"
                @class([
                    'relative w-full bg-white rounded-lg pl-3 pr-10 py-2 text-left focus:outline-hidden sm:text-sm h-10! disabled:bg-gray-100',
                    'border-error! ring-0!'                                                           => $errors->has($wireModel),
                    'border border-gray-950/10 focus:ring-1 focus:ring-primary focus:border-primary ' => !$suffix && !$prefix,
                ])
                type="button"
                role="combobox"
                aria-autocomplete="none"
                aria-label="{{ $label ?: $defaultOptionLabel }}"
                @unless ($labeless)
                    aria-labelledby="{{ $labelId }}"
                @endunless
                tabindex="0"
                x-on:click="openList()"
                x-on:keydown.arrow-down.stop.prevent="open ? onArrowDown() : openList()"
                x-on:keydown.arrow-up.stop.prevent="open ? onArrowUp() : openList()"
                x-on:keydown.space.stop.prevent="open ? onOptionSelect() : openList()"
                x-on:keydown.enter.stop.prevent="open ? onOptionSelect() : openList()"
                x-on:keydown.escape="onEscape()"
                x-ref="button"
                @disabled($attributes->get('disabled'))
                :aria-expanded="open"
                aria-labelledby="{{ $labelId }}"
                aria-controls="{{ $listboxId }}"
                aria-haspopup="listbox"
                aria-required="{{ $attributes->get('required') ? 'true' : 'false' }}"
                aria-invalid="{{ $errors->has($wireModel) ? 'true' : 'false' }}"
                x-bind:class="{
                    'ring-1! ring-primary! border-primary!': open && ! suffix && ! prefix,
                }"
                wire:loading.attr="disabled"
            >
                <span
                    x-text="selected.name"
                    class="block truncate"
                    x-bind:class="{
                        'text-gray-500': ! selected.id,
                    }"
                >
                    {{ $initialValue ?: $defaultOptionLabel }}
                </span>

                <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                    <x-icons.selector class="h-5 w-5 text-gray-400" />
                </span>
            </button>

            @if ($suffix)
                <div
                    wire:loading.class="bg-gray-100"
                    class="flex min-w-10 items-center justify-center border-l border-gray-950/10 !p-0 !py-1.5 text-gray-500 hover:cursor-default"
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
            x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
            x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
            x-on:keydown.enter.stop.prevent="onOptionSelect()"
            x-on:click.away="open = false"
            class="ring-opacity-5 absolute z-10 max-h-56 w-full overflow-auto rounded-md bg-white text-base shadow-lg ring-1 ring-gray-200 focus:outline-hidden sm:text-sm"
            x-bind:class="{
                'mt-1': ! dropdownUp,
                'mb-1 bottom-full': dropdownUp,
            }"
            tabindex="-1"
            style="display: none"
            x-ref="selectBox"
        >
            <ul
                class="relative max-h-56 p-1 focus:outline-hidden"
                id="{{ $listboxId }}"
                role="listbox"
                x-max="1"
                x-ref="ul"
                tabindex="-1"
                x-on:keydown.enter.stop.prevent="onOptionSelect()"
                x-on:keydown.space.stop.prevent="onOptionSelect()"
                x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
                x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
                x-on:keydown.escape.stop.prevent="onEscape()"
                @unless ($labeless)
                    aria-labelledby="{{ $labelId }}"
                @endunless
                x-bind:aria-activedescendant="activeDescendant"
            >
                <template x-if="items.length === 0">
                    <li class="relative py-2 pr-4 pl-8 text-sm text-gray-900 select-none" role="option">
                        {{ $emptyLabel ?? 'Nenhum resultado encontrado' }}
                    </li>
                </template>

                <template x-if="items.length > 0">
                    <template x-for="(item, index) in items" :key="index">
                        <li
                            class="relative rounded-md py-2 pr-4 pl-8 text-sm text-gray-900 select-none hover:cursor-pointer"
                            role="option"
                            x-bind:aria-selected="selectedIndex === index ? 'true' : 'false'"
                            x-on:click="choose(index)"
                            x-on:mouseenter="activeIndex = index"
                            x-on:mouseleave="activeIndex = null"
                            x-bind:id="`${name}::${item.id}`"
                            x-bind:class="{
                                'bg-primary text-white': activeIndex === index,
                                'hover:bg-primary hover:text-white': activeIndex !== index,
                            }"
                        >
                            <span
                                x-state:on="Selected"
                                x-state:off="Not Selected"
                                class="block truncate p-0! font-normal"
                                x-bind:class="{
                                    'font-semibold': selected.id === item.id,
                                }"
                                x-text="item.name"
                            >
                            </span>

                            <span
                                class="absolute inset-y-0 left-0 mb-0.5 flex items-center pl-2.5 text-white"
                                x-show="selectedIndex === index && activeIndex === index && clearable"
                                style="display: none"
                            >
                                <x-icons.x-mark class="h-4 w-4" />
                            </span>

                            <span
                                class="text-primary absolute inset-y-0 left-0 mb-0.5 flex items-center pl-2.5 font-semibold"
                                x-show="selectedIndex === index && activeIndex !== index"
                                style="display: none"
                            >
                                <x-icons.check class="h-4 w-4" />
                            </span>
                        </li>
                    </template>
                </template>
            </ul>
        </div>
    </div>

    @if ($showError)
        @error($wireModel)
            <x-ui.input.error :id="$id . '-error'" :message="$message" />
        @enderror
    @endif

    @if ($helperText)
        <span class="text-sm break-words text-gray-500">{{ $helperText }}</span>
    @endif
</div>

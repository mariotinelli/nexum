@props([
    'name',
    'route',
    'withInfinityScroll' => true,
    'initialValue'       => null,
    'withSearch'         => true,
    'id'                 => null,
    'label'              => null,
    'wire'               => null,
    'labeless'           => false,
    'showError'          => true,
    'defaultOptionLabel' => 'Selecione uma opção',
    'helperText'         => null,
    'hint'               => null,
    'prefix'             => null,
    'suffix'             => null,
    'selectedColumn'     => 'id',
    'params'             => [],
    'parentClass'        => null,
])

@php
    use Illuminate\Support\Facades\View;

    $name ??= $attributes->wire('model')->value();
    $id        = $id ?? $name;
    $wireModel = $attributes->whereStartsWith('wire:model')->first();

    $isLive = !isset($attributes->getAttributes()['wire:model']);
@endphp

<div
    x-data="selectSearch({
    search: null,
    initialValue: '{{ $initialValue }}',
    value: @entangle($wireModel).live,
    wireModel: '{{ $wireModel }}',
    open: false,
    withInfinityScroll: '{{ $withInfinityScroll ? 1 : 0 }}',
    name: '{{ $name }}',
    route: '{{ $route }}',
    withSearch: '{{ $withSearch ? 1 : 0 }}',
    defaultOptionLabel: {{ json_encode($defaultOptionLabel) }},
    selectedColumn: '{{ $selectedColumn }}',
    suffix: {{ $suffix ? 1 : 0 }},
    prefix: {{ $prefix ? 1 : 0 }},
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
                'flex items-center cursor-default h-10! rounded-lg',
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
                    wire:loading.class="bg-gray-100!"
                    class="flex min-w-10 items-center justify-center border-r border-r-gray-950/10 bg-white p-0! py-1.5! text-gray-500 hover:cursor-default"
                >
                    {{ $prefix }}
                </div>
            @endif

            <button
                id="{{ $id }}"
                @class([
                    'relative w-full bg-white rounded-lg pl-3 pr-10 py-2 text-left focus:outline-hidden sm:text-sm h-10! disabled:bg-gray-100',
                    'border-error! ring-0!'                                                          => $errors->has($wireModel),
                    'border border-gray-950/10 focus:ring-1 focus:ring-primary focus:border-primary' => !$suffix && !$prefix,
                ])
                type="button"
                x-on:click="openList()"
                x-on:keydown.arrow-down.stop.prevent="openList()"
                x-on:keydown.arrow-up.stop.prevent="openList()"
                x-on:keydown.space.stop.prevent="openList()"
                x-ref="button"
                @disabled($attributes->get('disabled'))
                :aria-expanded="open"
                aria-labelledby="listbox-label"
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
                    <x-icons.loading x-show="loading" class="h-5 w-5 animate-spin text-gray-400" />
                    <x-icons.selector x-show="! loading" class="h-5 w-5 text-gray-400" />
                </span>
            </button>

            @if ($suffix)
                <div
                    wire:loading.class="bg-gray-100!"
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
            x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
            x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
            x-on:keydown.enter.stop.prevent="onOptionSelect()"
            x-on:click.away="open = false"
            class="ring-opacity-5 absolute z-10 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-gray-200 focus:outline-hidden sm:text-sm"
            x-bind:class="{
                'mt-1': ! dropdownUp,
                'mb-1 bottom-full': dropdownUp,
            }"
            x-on:scroll="infinityScroll()"
            tabindex="-1"
            style="display: none"
            x-ref="searchBox"
        >
            @if ($withSearch)
                <div class="relative flex cursor-default items-center gap-1 shadow-xs">
                    <label x-bind:for="`search-${name}`">
                        <x-icons.search-circle class="h-7 w-7 pb-0.5 pl-2 text-gray-500" />
                    </label>
                    <input
                        type="text"
                        x-bind:id="`search-${name}`"
                        x-model="search"
                        x-on:input.debounce="doSearch()"
                        x-on:keydown.tab.stop.prevent="selectSearchFocus()"
                        x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
                        x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
                        x-on:keydown.enter.stop.prevent="onOptionSelect()"
                        class="w-full border-0 py-2 focus:ring-0 focus-visible:outline-hidden"
                        x-ref="search"
                        placeholder="Search ..."
                    />
                </div>
            @endif

            <ul
                class="p-1 relative {{ $withSearch ? 'max-h-44' : 'max-h-60' }} overflow-auto focus:outline-hidden"
                role="listbox"
                x-max="1"
                x-ref="ul"
                x-on:keydown.enter.stop.prevent="onOptionSelect()"
                x-on:keydown.space.stop.prevent="onOptionSelect()"
                x-on:keydown.arrow-up.stop.prevent="onArrowUp()"
                x-on:keydown.arrow-down.stop.prevent="onArrowDown()"
                x-on:scroll="infinityScroll()"
                aria-labelledby="listbox-label"
                x-bind:aria-activedescendant="activeDescendant"
            >
                <template x-if="items.length === 0">
                    <li class="relative pt-3 pr-4 pb-2 pl-8 text-sm text-gray-900 select-none" role="option">
                        Nenhum resultado encontrado
                    </li>
                </template>

                <template x-if="items.length > 0">
                    <template x-for="(item, index) in items" :key="index">
                        <li
                            class="hover:bg-primary relative rounded-md py-2 pr-4 pl-8 text-sm text-gray-900 select-none hover:cursor-pointer hover:text-white"
                            role="option"
                            x-on:click="selectedIndex === index ? remove() : choose(index)"
                            x-on:mouseenter="activeIndex = index"
                            x-on:mouseleave="activeIndex = null"
                            x-bind:id="`${name}::${item.id}}`"
                            x-bind:class="{
                                'bg-primary text-white': activeIndex === index,
                                'font-semibold': activeIndex === index || selected.id === item.id,
                                'text-gray-900': activeIndex !== index,
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
                                x-show="selectedIndex === index && activeIndex === index"
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
            <x-ui.input.error :message="$message" />
        @enderror
    @endif

    @if ($helperText)
        <span class="text-sm break-words text-gray-500">{{ $helperText }}</span>
    @endif
</div>

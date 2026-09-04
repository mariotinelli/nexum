@props([
    'route',
    'name',
    'icon',
    'prefix' => null,
])

<li
    @click.stop=""
    id="sidebar-link-{{ str($route)->replace('.', '-') }}"
    @class([
        'min-w-[56px] w-full hover:cursor-pointer hover:bg-secondary/50 rounded-lg text-gray-700 hover:cursor-pointer transition-all duration-300 ease-linear',
        'bg-secondary/50 text-primary' => request()->routeIs($route) || ($prefix && str_contains(request()->route()->getName(), $prefix)),
    ])
    x-bind:class="{ 'tooltip tooltip-bottom': ! asideOpen }"
    data-tip="{{ $name }}"
>
    <a
        wire:navigate
        href="{{ route($route) }}"
        class="hover:bg-secondary/50 hover:text-primary flex items-center gap-2 rounded-lg px-4 py-2.5"
    >
        <x-dynamic-component :component="'icons.' . $icon" class="h-5.5 min-h-5.5 w-5.5 min-w-5.5 font-medium" />
        <span
            x-show="asideOpen"
            class="overflow-hidden text-sm font-semibold text-nowrap text-ellipsis"
        >{{ $name }}</span>
    </a>
</li>

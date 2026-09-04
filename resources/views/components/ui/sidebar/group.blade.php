@props([
    'name',
    'open' => true,
])

<li
    id="group-{{ Str::slug($name) }}"
    x-data="{ expanded: @js($open) }"
    @click="expanded = ! expanded"
    class="list-none text-gray-700 hover:cursor-pointer"
>
    <div>
        <div class="flex items-center justify-between px-4 pb-3" x-show="asideOpen">
            <span class="font-medium text-gray-500">{{ $name }}</span>
            <x-icons.chevron-up
                class="h-4 w-4 transition-all duration-600 ease-linear"
                x-bind:class="expanded ? '' : 'rotate-180'"
            />
        </div>

        <ul
            class="relative space-y-1"
            x-show="expanded || ! asideOpen"
            x-collapse.duration.200ms
            x-bind:class="asideOpen ? 'ml-7 px-2' : 'px-4'"
        >
            <span x-show="expanded" class="absolute top-0 bottom-0 left-0 w-px bg-gray-300"></span>

            {{ $slot }}
        </ul>
    </div>
</li>

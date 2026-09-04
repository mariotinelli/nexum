@props([
    'group',
    'groupKey',
])

<div
    class="relative flex items-center bg-slate-50"
    x-bind:class="{ 'border-b': open }"
    x-data="{ left: 0 }"
    x-init="$nextTick(() => (left = $refs.checkbox.offsetWidth))"
>
    <div class="flex w-fit items-center gap-2 px-4 py-3" x-ref="checkbox">
        <x-ui.input.checkbox
            name="permissions-{{ $groupKey }}"
            sm
            x-bind:checked="allSelected"
            :label="$group->label"
            @change="selectGroup($event.target.checked)"
        />

        <div
            x-show="count > 0"
            class="flex items-center gap-1 rounded-full border border-gray-200 px-3 py-0.5 text-xs font-semibold"
        >
            <span x-text="count"></span>
            <span>/</span>
            <span>{{ count($group->permissions ?? collect($group->group)->pluck('permissions')->flatten()->toArray()) }}</span>
        </div>
    </div>

    <div
        id="open-group-permissions"
        class="absolute inset-0 flex items-center justify-end pr-2 hover:cursor-pointer"
        :style="`left: ${left}px`"
        @click="open = ! open"
    >
        <x-ui.button xs ghost class="w-fit" id="button-group-permissions-{{ $groupKey }}">
            <x-icons.chevron-down
                class="h-4 w-4 text-slate-400 transition-transform duration-200 hover:cursor-pointer"
                x-bind:class="open ? 'rotate-180' : ''"
            />
        </x-ui.button>
    </div>
</div>

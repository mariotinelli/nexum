@props([
    'title',
    'value',
])

<div class="flex min-w-0 flex-col">
    <span class="text-xs tracking-wider text-gray-500 uppercase">{{ $title }}</span>
    <span class="text-base font-medium break-all text-gray-900">{{ $value }}</span>
</div>

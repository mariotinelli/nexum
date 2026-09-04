@props([
    'title',
    'description',
    'actions' => null,
])

<div class="mb-6 sm:flex sm:items-center sm:justify-between">
    <div class="sm:flex-auto">
        <h1 class="text-primary text-2xl leading-6 font-semibold">{{ $title }}</h1>
        <p class="mt-2 text-sm text-gray-700">{{ $description }}</p>
    </div>

    @if ($actions)
        <div class="flex items-center gap-3">{{ $actions }}</div>
    @endif
</div>

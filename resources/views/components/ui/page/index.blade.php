@props([
    'title',
    'breadcrumb',
    'description'   => null,
    'headerActions' => null,
    'widgets'       => null,
    'contentClass'  => null,
])

<div>
    <x-ui.breadcrumb :items="$breadcrumb" />

    <x-ui.page.header :title="$title" :description="$description" :actions="$headerActions" />

    @if ($widgets)
        <x-ui.page.widgets> {{ $widgets }} </x-ui.page.widgets>
    @endif

    <div class="mt-6 {{ $contentClass }}">{{ $slot }}</div>
</div>

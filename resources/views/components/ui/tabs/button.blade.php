@props([
    'active'     => false,
    'icon'       => null,
    'neutral'    => false,
    'primary'    => false,
    'secondary'  => false,
    'accent'     => false,
    'success'    => false,
    'warning'    => false,
    'info'       => false,
    'error'      => false,
    'activeWhen' => null,
])

@php
    $resolvedActiveClass = match (true) {
        $neutral   => 'bg-gray-200 text-gray-900',
        $secondary => 'bg-secondary/30 text-gray-900',
        $accent    => 'bg-accent/30 text-gray-900',
        $success   => 'bg-success/30 text-gray-900',
        $warning   => 'bg-warning/30 text-gray-900',
        $info      => 'bg-info/30 text-gray-900',
        $error     => 'bg-error/30 text-gray-900',
        $primary   => 'bg-primary/30 text-gray-900',
        default    => 'bg-primary/30 text-gray-900',
    };

    $inactiveStateClass = 'text-gray-600 hover:bg-gray-100 hover:text-gray-900';

    $hasActiveWhen = filled($activeWhen);

    $stateClasses = [];

    if ($active && !$hasActiveWhen && filled($resolvedActiveClass)) {
        $stateClasses[] = $resolvedActiveClass;
    }

    if (!$active && !$hasActiveWhen) {
        $stateClasses[] = $inactiveStateClass;
    }
@endphp

<button
    {{
        $attributes->class([
            'tab rounded-md px-4 py-2 text-sm font-medium transition',
            ...$stateClasses,
        ])->merge(['type' => 'button'])
    }}
    @if ($hasActiveWhen)
        x-bind:class="{ '{{ $resolvedActiveClass }}': {{ $activeWhen }}, '{{ $inactiveStateClass }}': ! ({{ $activeWhen }}) }"
    @endif
>
    @if ($icon)
        <x-dynamic-component :component="'icons.' . $icon" class="me-2 size-5" />
    @endif

    <span>{{ $slot }}</span>
</button>

@props([
    'title'     => null,
    'neutral'   => false,
    'primary'   => false,
    'secondary' => false,
    'accent'    => false,
    'success'   => false,
    'warning'   => false,
    'info'      => false,
    'error'     => false,
    'white'     => false,
    'color'     => null,
])

<div @class([
    'bg-gray-50 border-l-4 p-4 rounded-md border-y border-y-gray-200 border-r border-r-gray-200',
    'border-neutral'   => $neutral || $color == 'neutral',
    'border-primary'   => $primary || $color == 'primary',
    'border-secondary' => $secondary || $color == 'secondary',
    'border-accent'    => $accent || $color == 'accent',
    'border-success'   => $success || $color == 'success',
    'border-warning'   => $warning || $color == 'warning',
    'border-info'      => $info || $color == 'info',
    'border-error'     => $error || $color == 'error',
])>
    <p class="text-sm text-gray-600">
        @if ($title)
            <div class="pb-2">
                <x-ui.title sm> {{ $title }} </x-ui.title>
            </div>
        @endif
        {{ $slot }}
    </p>
</div>

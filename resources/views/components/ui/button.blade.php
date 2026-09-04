@props([
    'label'        => null,
    'neutral'      => false,
    'primary'      => false,
    'secondary'    => false,
    'accent'       => false,
    'success'      => false,
    'warning'      => false,
    'info'         => false,
    'error'        => false,
    'white'        => false,
    'hover'        => false,
    'ghost'        => false,
    'link'         => false,
    'active'       => false,
    'outline'      => false,
    'noAnimation'  => false,
    'xs'           => false,
    'sm'           => false,
    'md'           => false,
    'lg'           => false,
    'wide'         => false,
    'block'        => false,
    'circle'       => false,
    'square'       => false,
    'loading'      => null,
    'icon'         => null,
    'withLoading'  => true,
    'href'         => false,
    'rightIcon'    => false,
    'uppercase'    => false,
    'soft'         => false,
    'inputAction'  => false,
    'cancelButton' => false,
    'navigate'     => true,
])

@php
    $loadingTarget = null;

    if ($wireClick = $attributes->get('wire:click')) {
        $loadingTarget = $wireClick;
    }

    if ($loading) {
        $loadingTarget = $loading;
    }

    $accessibleName = $label ?: trim($slot);
@endphp

@if ($href)
    <a href="{{ $href }}"
       @if($navigate) wire:navigate @endif
       @if(!$accessibleName && $icon) aria-label="{{ $icon }}" @endif
@else
    <button
        @if (!$accessibleName && $icon) aria-label="{{ $icon }}" @endif
        wire:loading.attr="disabled"
        @endif
        {{
            $attributes->class([
                'btn normal-case rounded-sm flex items-center',
                'btn-neutral'                                                                                                                  => $neutral,
                'btn-primary'                                                                                                                  => $primary,
                'btn-secondary'                                                                                                                => $secondary,
                'btn-accent'                                                                                                                   => $accent,
                'btn-success'                                                                                                                  => $success,
                'btn-warning'                                                                                                                  => $warning,
                'btn-info'                                                                                                                     => $info,
                'btn-error'                                                                                                                    => $error,
                'btn-hover'                                                                                                                    => $hover,
                'btn-ghost'                                                                                                                    => $ghost,
                'btn-link'                                                                                                                     => $link,
                'btn-active'                                                                                                                   => $active,
                'btn-outline'                                                                                                                  => $outline,
                'no-animation'                                                                                                                 => $noAnimation,
                'btn-xs'                                                                                                                       => $xs,
                'btn-sm'                                                                                                                       => $sm,
                'btn-md'                                                                                                                       => $md || (!$xs && !$sm && !$lg),
                'btn-lg'                                                                                                                       => $lg,
                'btn-wide'                                                                                                                     => $wide,
                'btn-block'                                                                                                                    => $block,
                'btn-circle!'                                                                                                                  => $circle,
                'btn-square'                                                                                                                   => $square,
                'bg-white text-gray-900 hover:bg-white hover:text-gray-900 disabled:text-[#B8BFC3] disabled:border-none border-gray-300'       => $white,
                'uppercase! tracking-wider! text-xs! font-bold!'                                                                               => $uppercase,
                'btn-soft'                                                                                                                     => $soft,
                'btn-ghost hover:bg-gray-100'                                                                                                  => $cancelButton,
                'border-0! shadow-none! bg-transparent! hover:bg-transparent! hover:border-0! hover:outline-0! focus:outline-0! focus:ring-0!' => $inputAction,
            ])->merge(['type' => 'button'])
        }}
    >
        @if ($icon && !$rightIcon)
        <x-dynamic-component :component="'icons.' . $icon" class="size-4!" aria-hidden="true" />

@endif

@if ($accessibleName)
    <span>{{ $label ?: $slot }}</span>
@endif

@if ($icon && $rightIcon)
    <x-dynamic-component :component="'icons.' . $icon" class="size-4!" aria-hidden="true" />
@endif

@if ($withLoading && $loadingTarget)
    <span
        wire:loading.class.remove="hidden"
        wire:target="{{ $loadingTarget }}"
        class="loading loading-spinner loading-xs hidden"
        aria-hidden="true"
    ></span>

    <span class="sr-only" wire:loading wire:target="{{ $loadingTarget }}"> Carregando... </span>
@endif

@if ($href)
    </a>
@else
    </button>
@endif

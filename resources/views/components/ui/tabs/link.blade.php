@props([
    'name',
    'active' => false,
    'key'    => $key ?? 'lists_tab',
    'icon'   => null,
    'value'  => null,
])

@php
    $tabValue = $value ?? str($name)->slug();
    $tabId    = 'tab-' . $key . '-' . $tabValue;
    $panelId  = 'tabpanel-' . $key . '-' . $tabValue;
@endphp

<button
    type="button"
    @class([
        'tab',
        'text-nowrap checked:bg-primary/20' => !$icon,
    ])
    id="{{ $tabId }}"
    data-ui-tab
    role="tab"
    aria-controls="{{ $panelId }}"
    aria-selected="{{ $active ? 'true' : 'false' }}"
    tabindex="{{ $active ? '0' : '-1' }}"
    aria-label="{{ $name }}"
    {{ $attributes }}
>
    @if ($icon)
        <x-dynamic-component :component="'icons.' . $icon" class="me-2 size-4" />
    @endif

    {{ $name }}
</button>

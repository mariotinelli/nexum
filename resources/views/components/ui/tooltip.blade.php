@props([
    'label'     => null,
    'open'      => false,
    'top'       => false,
    'bottom'    => false,
    'left'      => false,
    'right'     => false,
    'primary'   => false,
    'secondary' => false,
    'accent'    => false,
    'info'      => false,
    'success'   => false,
    'warning'   => false,
    'error'     => false,
    'position'  => null,
])

@php
    $tooltipId = 'tooltip-' . str()->ulid();
@endphp

<div
    x-data="{
        tooltipLabel: {{ Js::from($label) }},
        isOpen: {{ $open ? 'true' : 'false' }},
        openDelayTimer: null,
        closeDelayTimer: null,
        useSelfAsTrigger: false,
        initA11y() {
            const focusableChild = this.$el.querySelector('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex=\'-1\'])');

            if (focusableChild) {
                this.$el.removeAttribute('tabindex');
                this.$el.removeAttribute('aria-describedby');
                focusableChild.setAttribute('aria-describedby', '{{ $tooltipId }}');
                this.useSelfAsTrigger = false;

                return;
            }

            this.$el.setAttribute('tabindex', '0');
            this.$el.setAttribute('aria-describedby', '{{ $tooltipId }}');
            this.useSelfAsTrigger = true;
        },
        openWithDelay() {
            if (this.closeDelayTimer) {
                clearTimeout(this.closeDelayTimer);
            }

            this.openDelayTimer = setTimeout(() => {
                this.isOpen = true;
            }, 150);
        },
        closeTooltip() {
            if (this.openDelayTimer) {
                clearTimeout(this.openDelayTimer);
            }

            this.closeDelayTimer = setTimeout(() => {
                this.isOpen = false;
            }, 50);
        },
        onEscape() {
            this.isOpen = false;

            if (this.$el.contains(document.activeElement)) {
                document.activeElement.blur();
            }
        },
        init() {
            this.initA11y();
        }
    }"
    @mouseenter="openWithDelay()"
    @mouseleave="closeTooltip()"
    @focusin="openWithDelay()"
    @focusout="closeTooltip()"
    @keydown.escape.stop.prevent="onEscape()"
    @keydown.escape.window.stop.prevent="onEscape()"
    @class([
        "tooltip cursor-pointer",
        "tooltip-top"       => $top || $position === "top",
        "tooltip-bottom"    => $bottom || $position === "bottom",
        "tooltip-left"      => $left || $position === "left",
        "tooltip-right"     => $right || $position === "right",
        "tooltip-primary"   => $primary,
        "tooltip-secondary" => $secondary,
        "tooltip-accent"    => $accent,
        "tooltip-info"      => $info,
        "tooltip-success"   => $success,
        "tooltip-warning"   => $warning,
        "tooltip-error"     => $error,
    ])
    x-bind:class="{ 'tooltip-open': isOpen }"
    x-bind:data-tip="isOpen ? tooltipLabel : ''"
>
    <span id="{{ $tooltipId }}" role="tooltip" class="sr-only">{{ $label }}</span>
    {{ $slot }}
</div>

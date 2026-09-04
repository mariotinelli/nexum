@props([
    'trigger',
    'header' => null,
    'end'    => false,
    'top'    => false,
    'bottom' => false,
    'left'   => false,
    'right'  => false,
    'hover'  => false,
    'open'   => false,
    'sm'     => false,
    'md'     => false,
    'lg'     => false,
    'width'  => 'w-52',
])

@php
    $uuid = bin2hex(random_bytes(4));
@endphp

<div
    x-data="{
        open: {{ $open ? 'true' : 'false' }},
        get triggerElement() {
            return this.$refs.trigger?.querySelector('button, a, [role=button]');
        },
        toggle(event) {
            event?.preventDefault();
            this.open = ! this.open;
        },
        close() {
            this.open = false;

            const trigger = this.triggerElement;
            trigger?.blur();
        },
        syncTriggerAria() {
            const trigger = this.triggerElement;
            if (! trigger) {
                return;
            }

            trigger.setAttribute('aria-haspopup', 'menu');
            trigger.setAttribute('aria-controls', 'dropdown-menu-{{ $uuid }}');
            trigger.setAttribute('aria-expanded', this.open ? 'true' : 'false');
        },
        bindTriggerEvents() {
            const trigger = this.triggerElement;
            if (! trigger) {
                return;
            }

            trigger.addEventListener('click', (event) => this.toggle(event));
            trigger.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    this.toggle(event);
                }

                if (event.key === 'Escape') {
                    event.preventDefault();
                    this.close();
                }
            });
        },
        init() {
            this.syncTriggerAria();
            this.bindTriggerEvents();

            this.$watch('open', () => this.syncTriggerAria());
        }
    }"
    :class="{ 'dropdown-open': open }"
    @click.outside="close()"
    @keydown.escape.window.stop.prevent="close()"
    @class([
        'dropdown relative z-40 overflow-visible',
        'dropdown-end'    => $end,
        'dropdown-top'    => $top,
        'dropdown-bottom' => $bottom,
        'dropdown-left'   => $left,
        'dropdown-right'  => $right,
        'dropdown-hover'  => $hover,
    ])
>
    <span x-ref="trigger"> {{ $trigger }} </span>

    <div
        @keydown.escape.window="close()"
        @class([
            "dropdown-content bg-base-100 rounded-md mt-1 {$width} p-1 pb-0 shadow-md text-gray-800 ring-1 ring-gray-200 z-[9999]!",
            'divide-y divide-gray-200' => $header,
            'w-64!'                    => $sm,
            'w-80!'                    => $md,
            'w-96!'                    => $lg,
        ])
        tabindex="-1"
    >
        @if ($header)
            <div class="p-2" role="none">{{ $header }}</div>
        @endif

        <ul class="space-y-1 py-2" role="menu" id="dropdown-menu-{{ $uuid }}">
            {{ $slot }}
        </ul>
    </div>
</div>

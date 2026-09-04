@props([
    'header'      => null,
    'footer'      => null,
    'description' => null,
    'sm'          => false,
    'md'          => false,
    'lg'          => false,
    'xl'          => false,
    'xl2'         => false,
    'xl3'         => false,
    'xl4'         => false,
    'xl5'         => false,
    'xl6'         => false,
    'xl7'         => false,
])

@php
    $titleId = 'slide-over-title-' . str()->ulid();
@endphp

<div>
    <div
        class="relative z-50 bg-gray-100"
        x-data="{
            open: @entangle('sidepageOpen').live,
            lastFocusedElement: null,
            getFocusableElements() {
                if (! this.$refs.panel) {
                    return [];
                }

                return Array.from(this.$refs.panel.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex=\'-1\'])'));
            },
            getInputElements() {
                if (! this.$refs.panel) {
                    return [];
                }

                return Array.from(this.$refs.panel.querySelectorAll('input:not([type=\'hidden\']):not([disabled]), select:not([disabled]), textarea:not([disabled])'));
            },
            focusFirstElement() {
                const inputElements = this.getInputElements();

                if (inputElements.length > 0) {
                    inputElements[0].focus({ preventScroll: true });

                    if (document.activeElement !== inputElements[0]) {
                        requestAnimationFrame(() => {
                            inputElements[0].focus({ preventScroll: true });
                        });
                    }

                    return;
                }

                const focusableElements = this.getFocusableElements();

                if (focusableElements.length > 0) {
                    focusableElements[0].focus({ preventScroll: true });

                    if (document.activeElement !== focusableElements[0]) {
                        requestAnimationFrame(() => {
                            focusableElements[0].focus({ preventScroll: true });
                        });
                    }

                    return;
                }

                this.$refs.panel?.focus({ preventScroll: true });
            },
            trapFocus(event) {
                if (! this.open || event.key !== 'Tab') {
                    return;
                }

                const focusableElements = this.getFocusableElements();

                if (focusableElements.length === 0) {
                    event.preventDefault();
                    this.$refs.panel?.focus();
                    return;
                }

                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];

                if (event.shiftKey && document.activeElement === firstElement) {
                    event.preventDefault();
                    lastElement.focus();
                    return;
                }

                if (! event.shiftKey && document.activeElement === lastElement) {
                    event.preventDefault();
                    firstElement.focus();
                }
            },
            closePanel() {
                this.open = false;
            },
            init() {
                this.$watch('open', (isOpen) => {
                    if (isOpen) {
                        this.lastFocusedElement = document.activeElement;

                        this.$nextTick(() => {
                            this.focusFirstElement();

                            setTimeout(() => {
                                if (this.open) {
                                    this.focusFirstElement();
                                }
                            }, 320);
                        });

                        return;
                    }

                    this.$nextTick(() => {
                        if (this.lastFocusedElement && typeof this.lastFocusedElement.focus === 'function') {
                            this.lastFocusedElement.focus();
                        }
                    });
                });
            }
        }"
        @keydown.window.escape.stop.prevent="closePanel()"
        @keydown.tab="trapFocus($event)"
        x-show="open"
        role="dialog"
        aria-labelledby="{{ $titleId }}"
        x-ref="dialog"
        aria-modal="true"
    >
        <div
            x-show="open"
            class="fixed inset-0 bg-gray-900/65"
            aria-hidden="true"
            x-transition:enter="transition-opacity ease-linear duration-300"
            x-transition:enter-start="opacity-0"
            x-transition:enter-end="opacity-100"
            x-transition:leave="transition-opacity ease-linear duration-300"
            x-transition:leave-start="opacity-100"
            x-transition:leave-end="opacity-0"
        ></div>

        <div class="fixed inset-0 overflow-hidden">
            <div class="absolute inset-0 overflow-hidden">
                <div @class([
                    'pointer-events-none fixed inset-y-0 right-0 flex max-w-full',
                    'pl-10 sm:pl-16' => $sm || $md || $lg || $xl || $xl2 || $xl3 || $xl4 || $xl5 || $xl6 || $xl7,
                ])>
                    <div
                        x-show="open"
                        x-transition:enter="transform transition ease-in-out duration-300"
                        x-transition:enter-start="translate-x-full"
                        x-transition:enter-end="translate-x-0"
                        x-transition:leave="transform transition ease-in-out duration-300"
                        x-transition:leave-start="translate-x-0"
                        x-transition:leave-end="translate-x-full"
                        @click.away="closePanel()"
                        x-ref="panel"
                        tabindex="-1"
                        @class([
                            'pointer-events-auto w-screen',
                            'max-w-sm'  => $sm,
                            'max-w-md'  => $md,
                            'max-w-lg'  => $lg,
                            'max-w-xl'  => $xl,
                            'max-w-2xl' => $xl2,
                            'max-w-3xl' => $xl3,
                            'max-w-4xl' => $xl4,
                            'max-w-5xl' => $xl5,
                            'max-w-6xl' => $xl6,
                            'max-w-7xl' => $xl7,
                        ])
                    >
                        <div class="flex h-full flex-col divide-y divide-gray-200 bg-white shadow-xl">
                            @if ($header)
                                <div class="bg-primary h-(--navbar-height) px-4 py-6 sm:px-6">
                                    <div class="flex items-center justify-between">
                                        <h2 class="text-base font-semibold text-white" id="{{ $titleId }}">
                                            {{ $header }}
                                        </h2>
                                        <div class="ml-3 flex h-7 items-center">
                                            <button
                                                type="button"
                                                class="relative"
                                                aria-label="Fechar painel"
                                                @click="closePanel()"
                                            >
                                                <span class="sr-only">Fechar painel</span>
                                                <x-icons.x-mark
                                                    class="h-6 w-6 text-white hover:cursor-pointer"
                                                    aria-hidden="true"
                                                />
                                            </button>
                                        </div>
                                    </div>

                                    @if ($description)
                                        <div class="mt-1">
                                            <p class="text-sm text-white">{{ $description }}</p>
                                        </div>
                                    @endif
                                </div>
                            @endif

                            @unless ($header)
                                <h2 id="{{ $titleId }}" class="sr-only">Painel lateral</h2>
                            @endunless

                            <div class="h-0 flex-1 overflow-y-auto">{{ $slot }}</div>

                            @if ($footer)
                                <div class="flex shrink-0 justify-end px-4 py-4">{{ $footer }}</div>
                            @endif
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

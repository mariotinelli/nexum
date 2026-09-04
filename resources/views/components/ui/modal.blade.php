@props([
    'id',
    'title'       => '',
    'description' => '',
    'footer'      => '',
    'lg'          => false,
    'xl'          => false,
    'xl2'         => false,
    'xl3'         => false,
    'clickAway'   => true,
    'divided'     => false,
    'headerAlign' => 'left',
    'scrollable'  => false,
    'closeButton' => true,
    'escapable'   => true,
    'manual'      => false,
])

<div
    id="{{ $id }}"
    x-data="{
        open: @if($manual) false @elseif(isset($__livewire)) @entangle('modalOpen') @else false @endif,
        modalId: '{{ $id }}',
        clickAway: @js($clickAway),
        escapable: @js($escapable),
        trigger: null,
        init() {
            this.$watch('open', (value) => {
                if (value) {
                    this.trigger = document.activeElement;
                    this.focusInput();
                } else {
                    this.modalEvent();
                    this.$nextTick(() => this.trigger?.focus());
                }
            })
            if (this.open) {
                this.focusInput()
            }
        },
        modalEvent() {
            $dispatch('modal-closed', { modal: '{{ $id ?: md5($title) }}' })
        },
        focusInput() {
            this.$nextTick(() => {
                const inputs = this.$refs.slot.querySelectorAll('input, select, textarea, button, a[href]')
                inputs[0]?.focus();
            });
        },
        trapFocus(event) {
            const focusable = this.$refs.modal.querySelectorAll(`input, select, textarea, button, a[href], [tabindex]:not([tabindex='-1'])`);
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (event.shiftKey) {
                if (document.activeElement === first) {
                    event.preventDefault();
                    last.focus();
                }
            } else {
                if (document.activeElement === last) {
                    event.preventDefault();
                    first.focus();
                }
            }
        }
    }"
    @keydown.window.escape="escapable && open ? (open = false) : null"
    @keydown.tab="open ? trapFocus($event) : null"
    @open-modal.window="$event.detail === modalId ? (open = true) : null"
    @close-modal.window="$event.detail === modalId ? (open = false) : null"
    x-show="open"
    class="relative z-15"
    role="dialog"
    aria-labelledby="{{ $id ?: md5($title) }}-title"
    aria-label="{{ $title }}"
    aria-modal="true"
    x-cloak
>
    <div
        x-show="open"
        x-transition:enter="ease-out duration-300"
        x-transition:enter-start="opacity-0"
        x-transition:enter-end="opacity-100"
        x-transition:leave="ease-in duration-200"
        x-transition:leave-start="opacity-100"
        x-transition:leave-end="opacity-0"
        class="fixed inset-0 bg-gray-500/75 transition-opacity"
        aria-hidden="true"
    ></div>

    <div x-show="open" class="fixed inset-0 z-15 w-screen">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
            <div
                x-show="open"
                x-ref="modal"
                x-transition:enter="ease-out duration-300"
                x-transition:enter-start="opacity-0 scale-95"
                x-transition:enter-end="opacity-100 scale-100"
                x-transition:leave="ease-in duration-200"
                x-transition:leave-start="opacity-100 scale-100"
                x-transition:leave-end="opacity-0 translate-y-0 scale-95"
                @click.window.outside="clickAway && open ? (open = false) : null"
                @class([
                    'w-full max-w-lg bg-white relative transform rounded-xl shadow-xl p-0
                        pointer-events-auto relative transition-all flex flex-col items-start justify-start',
                    'max-w-2xl!'               => $lg,
                    'max-w-4xl!'               => $xl,
                    'max-w-6xl!'               => $xl2,
                    'max-w-7xl!'               => $xl3,
                    'divide-y divide-gray-200' => $divided,
                ])
            >
                @if ($closeButton)
                    <button
                        class="absolute top-1 right-1 border-none bg-transparent p-2 shadow-none hover:cursor-pointer"
                        type="button"
                        @click="open = false"
                    >
                        <span class="sr-only">Fechar modal</span>
                        <x-icons.x-mark class="size-5! bg-none text-gray-500" aria-hidden="true" />
                    </button>
                @endif

                <div @class([
                    'flex flex-col px-6 pt-6 pb-3 w-full justify-start',
                    'items-start'  => $headerAlign === 'left',
                    'items-center' => $headerAlign === 'center',
                    'items-end'    => $headerAlign === 'right',
                ])>
                    <h2 id="{{ $id ?: md5($title) }}-title" class="text-lg leading-6 font-semibold text-gray-950">
                        {{ $title }}
                    </h2>
                    <p class="text-sm text-gray-600">{{ $description }}</p>
                </div>

                <div
                    x-ref="slot"
                    @class([
                        'px-6 pb-3 w-full flex text-start',
                        'overflow-y-auto max-h-[calc(100vh-200px)]' => $scrollable,
                        'py-5!'                                     => $divided,
                    ])
                >
                    <div class="w-full">{{ $slot }}</div>
                </div>

                <div class="w-full overflow-hidden rounded-b-xl">
                    @if ($footer)
                        {{ $footer }}
                    @else
                        <div class="flex w-full items-center justify-end gap-2 bg-gray-100 p-3">
                            <x-ui.button
                                id="cancel-button"
                                label="Cancelar"
                                ghost
                                @click="open = false"
                                class="hover:bg-gray-100"
                            />
                            <x-ui.button id="save-button" label="Salvar" primary wire:click="save" />
                        </div>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>

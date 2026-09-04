<div>
    {{-- Desktop sidebar --}}
    <div>
        <div class="relative z-5 hidden bg-gray-100 lg:block" role="complementary" aria-label="Menu lateral">
            <button
                type="button"
                aria-label="Alternar menu lateral"
                aria-controls="desktop-sidebar-panel"
                x-bind:aria-expanded="asideOpen ? 'true' : 'false'"
                @click="
                    localStorage.setItem('asideOpen', ! asideOpen);
                    asideOpen = ! asideOpen;
                "
                @class([
                    'fixed sidebar-toggle transition-all duration-300 ease-linear shadow-lg bg-white
                        p-1.5 hover:text-white rounded-full border border-gray-300 hover:cursor-pointer
                        hover:bg-primary text-gray-700 z-20',
                    'top-[calc(var(--navbar-height)+var(--dev-bar-height)+.3rem)]' => withEnvBar(),
                    'top-[calc(var(--navbar-height)+.3rem)]'                       => !withEnvBar(),
                ])
                x-bind:class="
                    asideOpen
                        ? 'left-[calc(var(--open-sidebar-width)-1.1rem)]'
                        : 'left-[calc(var(--closed-sidebar-width)-1.1rem)]'
                "
            >
                <x-icons.chevron-left
                    class="h-[1.15rem] w-[1.15rem] font-bold transition-transform duration-600 ease-linear"
                    x-bind:class="asideOpen ? '' : 'rotate-180'"
                    aria-hidden="true"
                />
            </button>

            <div class="fixed inset-y-0 z-5 overflow-hidden">
                <div class="absolute inset-0 overflow-hidden">
                    <div class="pointer-events-none fixed inset-y-0 left-0 flex max-w-full">
                        <div
                            id="desktop-sidebar-panel"
                            class="pointer-events-auto w-screen transition-all duration-300 ease-linear"
                            x-bind:class="asideOpen ? 'max-w-(--open-sidebar-width)' : 'max-w-(--closed-sidebar-width)'"
                        >
                            <div class="flex h-full flex-col">
                                <div
                                    @class([
                                        'opacity-0',
                                        'h-[calc(var(--navbar-height)+var(--dev-bar-height))]' => withEnvBar(),
                                        'h-(--navbar-height)'                                  => !withEnvBar(),
                                    ])
                                ></div>

                                <div class="h-0 flex-1 bg-white pt-12 shadow-xl">
                                    <div class="h-full space-y-6 overflow-x-hidden overflow-y-auto pt-2">
                                        @include('livewire.partials.sidebar-groups')
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {{-- Mobile sidebar --}}
    <div>
        <div
            class="relative z-10 bg-gray-100"
            @keydown.window.escape="mobileAsideOpen = false"
            x-show="mobileAsideOpen"
            aria-labelledby="slide-over-title"
            x-ref="dialog"
            aria-modal="true"
        >
            <div class="fixed inset-0 z-15 overflow-hidden">
                <div class="absolute inset-0 overflow-hidden">
                    <div class="pointer-events-none fixed inset-y-0 left-0 flex max-w-full pr-10 sm:pr-16">
                        <div
                            id="mobile-sidebar-panel"
                            x-show="mobileAsideOpen"
                            x-transition:enter="transform transition ease-in-out duration-300"
                            x-transition:enter-start="-translate-x-full"
                            x-transition:enter-end="translate-x-0"
                            x-transition:leave="transform transition ease-in-out duration-300"
                            x-transition:leave-start="translate-x-0"
                            x-transition:leave-end="-translate-x-full"
                            @click.away="mobileAsideOpen = false"
                            class="pointer-events-auto w-screen max-w-(--mobile-sidebar-width)"
                        >
                            <div class="flex h-full flex-col divide-y divide-gray-200 bg-white shadow-xl">
                                <div class="bg-primary relative flex h-(--navbar-height) items-center justify-between px-8 shadow-sm sm:px-6">
                                    <x-ui.application-logo class="block h-9 w-auto" />

                                    <button
                                        type="button"
                                        class="absolute top-2 -right-8"
                                        aria-label="Fechar menu lateral"
                                        @click="mobileAsideOpen = false"
                                    >
                                        <x-icons.x-mark
                                            class="z-50 h-6 w-6 cursor-pointer text-white"
                                            aria-hidden="true"
                                        />
                                    </button>
                                </div>

                                <div class="h-0 flex-1 space-y-6 overflow-y-auto py-3">
                                    @include('livewire.partials.sidebar-groups')
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div
                x-show="mobileAsideOpen"
                class="fixed inset-0 bg-gray-900/65"
                x-transition:enter="transition-opacity ease-linear duration-300"
                x-transition:enter-start="opacity-0"
                x-transition:enter-end="opacity-100"
                x-transition:leave="transition-opacity ease-linear duration-300"
                x-transition:leave-start="opacity-100"
                x-transition:leave-end="opacity-0"
            ></div>
        </div>
    </div>
</div>

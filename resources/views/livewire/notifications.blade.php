<div>
    <div class="relative mr-2">
        <x-icons.bell
            id="open-notifications"
            class="block h-7 w-7 cursor-pointer text-white hover:text-gray-100"
            wire:click="openSidepage"
        />

        <x-ui.badge circle sm class="bg-secondary border-secondary text-dark absolute -top-3 -right-3 font-semibold">
            {{ $this->unreadNotifications->count() }}
        </x-ui.badge>
    </div>

    <x-ui.sidepage md>
        @if (count($this->notifications) === 0)
            <div class="max-w-smp-8 relative text-center">
                <div class="flex justify-end p-4">
                    <x-icons.x-mark
                        id="close-notifications"
                        class="z-50 h-6 w-6 cursor-pointer text-gray-600"
                        @click="open = false"
                    />
                </div>

                <div class="mb-6 flex items-center justify-center">
                    <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
                        <x-icons.bell-slash class="z-50 h-6 w-6 text-gray-400" />
                    </div>
                </div>

                <h2 class="mb-2 text-lg font-semibold text-gray-900">Sem notificações</h2>
                <p class="text-sm text-gray-500">Por favor, verifique mais tarde</p>
            </div>
        @else
            <div class="top-0 right-0 z-10 items-center border-b border-gray-300 bg-white p-4 pt-4">
                <div class="flex w-full justify-between">
                    <div class="relative">
                        <h1 class="text-lg font-semibold">Notificações</h1>
                        <x-ui.badge primary circle sm class="absolute top-0 -right-7">
                            {{ $this->unreadNotifications->count() }}
                        </x-ui.badge>
                    </div>
                    <x-icons.x-mark
                        id="close-notifications"
                        class="z-50 h-6 w-6 cursor-pointer text-gray-400"
                        @click="open = false"
                    />
                </div>
                <div class="mt-4 mb-3 flex">
                    <x-ui.button
                        id="mark-all-as-read"
                        primary
                        outline
                        xs
                        label="Marcar todas como lida"
                        wire:click="markAllAsRead"
                    />
                    <x-ui.button
                        id="delete-notifications"
                        error
                        outline
                        xs
                        label="Limpar"
                        wire:click="deleteAll"
                        class="ml-4"
                    />
                </div>
            </div>

            <div>
                @foreach ($this->notifications as $notification)
                    <x-notifications.item
                        :notification="$notification"
                        wire:key="notification-{{ $notification->id }}"
                    />
                @endforeach
            </div>
        @endif
    </x-ui.sidepage>
</div>

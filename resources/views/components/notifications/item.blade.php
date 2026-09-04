@props([
    'notification',
])

<div @class([
    $notification->data['color'] ?? 'border-primary',
    'border-l border-l-2' => is_null($notification->read_at),
])>
    <div class="items-center border-b border-gray-300 bg-white p-4">
        <div class="w-full items-center">
            <div class="mb-1 flex w-full justify-between">
                <div>
                    <div class="flex justify-between gap-3">
                        @isset($notification->data['icon'])
                            <x-dynamic-component
                                :component="'icons.' . $notification->data['icon']"
                                class="z-50 h-6 w-6 text-gray-400"
                            />
                        @endisset

                        <p class="font-semibold">{{ $notification->data['title'] }}</p>
                    </div>
                </div>

                <x-icons.x-mark
                    id="delete-notification-{{ $notification->id }}"
                    class="z-50 h-5 w-5 cursor-pointer text-gray-400"
                    wire:click="delete('{{ $notification->id }}')"
                />
            </div>

            <div>
                <p class="mb-1 pl-9 text-sm text-gray-500">
                    {{ $notification->created_at->translatedFormat('d \d\e F \d\e Y \à\s H:i') }}
                </p>

                @isset($notification->data['description'])
                    <p class="mb-2 pl-9 text-gray-700">{{ $notification->data['description'] }}</p>
                @endisset

                @isset($notification->data['details'])
                    <div class="mt-2 space-y-2 pl-9 text-sm">
                        @foreach ($notification->data['details'] as $label => $content)
                            <div class="flex space-x-1">
                                <div class="text-sm text-gray-700">{{ $label }}:</div>
                                <div class="font-semibold text-gray-700">{{ $content }}</div>
                            </div>
                        @endforeach
                    </div>
                @endisset

                @isset($notification->data['route'])
                    <div class="my-2 pl-9">
                        <a
                            href="{{ $notification->data['route']['url'] }}"
                            class="text-primary w-fit border-none bg-transparent text-sm font-bold underline hover:cursor-pointer"
                        >
                            {{ $notification->data['route']['action'] }}
                        </a>
                    </div>
                @endisset
            </div>
        </div>
    </div>
</div>

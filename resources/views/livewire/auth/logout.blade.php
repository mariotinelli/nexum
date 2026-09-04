<button
    type="button"
    x-on:click="$dispatch('toggle-loading', { loading: true })"
    wire:click="logout"
    class="flex w-full cursor-pointer items-center justify-start gap-2 rounded-lg p-2 text-base text-gray-500 hover:bg-gray-50 active:bg-gray-200"
>
    <x-icons.arrow-left-start-on-rectangle class="h-6 min-h-6 w-6 min-w-6" />
    Sair
</button>

<div x-data="{ show: false }">
    <x-ui.input {{ $attributes }} x-cloak x-bind:type="show ? 'text' : 'password'">
        <x-slot name="suffix">
            <x-icons.eye
                x-show="! show"
                @click="show = true"
                class="size-5 cursor-pointer text-gray-500 hover:text-gray-700"
            />

            <x-icons.eye-slash
                x-show="show"
                @click="show = false"
                class="size-5 cursor-pointer text-gray-500 hover:text-gray-700"
            />
        </x-slot>
    </x-ui.input>
</div>

<div class="flex w-full items-center justify-center bg-white p-8 md:w-1/2">
    <div class="w-full max-w-md rounded-lg border border-gray-300 bg-white p-8 shadow-lg md:p-10">
        <h2 class="mb-8 text-center text-xl font-bold text-gray-800">REDEFINIR SENHA</h2>

        @if (session('status'))
            <div class="mb-4 text-center text-sm font-medium text-green-600">{{ session('status') }}</div>
        @endif

        <form wire:submit.prevent="newPassword" class="space-y-5">
            <input type="hidden" name="token" wire:model="token" />

            <div>
                <x-ui.input
                    id="email"
                    label="Email"
                    name="email"
                    type="email"
                    wire:model="email"
                    required
                    autofocus
                    disabled
                    autocomplete="username"
                />
            </div>

            <div class="mt-4">
                <x-ui.input.password
                    id="password"
                    label="Senha"
                    name="password"
                    wire:model="password"
                    required
                    autocomplete="new-password"
                />
            </div>

            <div class="mt-4">
                <x-ui.input.password
                    id="password_confirmation"
                    label="Confirmar Senha"
                    name="password_confirmation"
                    wire:model="password_confirmation"
                    required
                    autocomplete="new-password"
                />
            </div>

            <div class="mt-6 flex items-center justify-end">
                <x-ui.button primary sm uppercase type="submit" loading="newPassword"> Redefinir Senha </x-ui.button>
            </div>
        </form>
    </div>
</div>

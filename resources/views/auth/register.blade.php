<x-guest-layout variant="split">
    <form method="POST" action="{{ route('register') }}">
        @csrf

        <div>
            <x-ui.input
                label="Nome"
                name="name"
                type="text"
                :value="old('name')"
                required
                autofocus
                autocomplete="name"
            />
        </div>

        <div class="mt-4">
            <x-ui.input
                label="Email"
                name="email"
                type="email"
                :value="old('email')"
                required
                autocomplete="username"
            />
        </div>

        <div class="mt-4">
            <x-ui.input label="Senha" name="password" type="password" required autocomplete="new-password" />
        </div>

        <div class="mt-4">
            <x-ui.input
                label="Confirmar Senha"
                name="password_confirmation"
                type="password"
                required
                autocomplete="new-password"
            />
        </div>

        <div class="mt-4 flex items-center justify-end">
            <a
                class="focus:ring-primary rounded-md text-sm text-gray-600 underline hover:text-gray-900 focus:ring-2 focus:ring-offset-2 focus:outline-hidden"
                href="{{ route('admin.login') }}"
            >
                Já está registrado?
            </a>

            <x-ui.button primary sm uppercase class="ms-4" type="submit"> Registrar </x-ui.button>
        </div>
    </form>
</x-guest-layout>

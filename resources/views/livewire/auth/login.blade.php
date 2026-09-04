<div class="flex flex-col gap-8">
    <div class="flex flex-col gap-2 text-center">
        <p class="text-primary text-sm font-semibold tracking-widest uppercase">Área administrativa</p>
        <h1 class="text-3xl font-bold text-gray-900">Entrar</h1>
        <p class="text-sm text-gray-600">Informe suas credenciais para acessar o sistema.</p>
    </div>

    <form wire:submit="login" class="flex flex-col gap-5">
        <x-ui.input label="Email" type="email" wire:model="email" required autofocus autocomplete="username" />

        <x-ui.input.password
            label="Senha"
            placeholder="Digite sua senha"
            wire:model="password"
            required
            autocomplete="current-password"
        />

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <x-ui.input.checkbox label="Lembrar-me" wire:model="remember" />

            <x-ui.button link :href="route('password.forgot')" sm> Esqueceu sua senha? </x-ui.button>
        </div>

        <x-ui.button primary block uppercase type="submit" loading="login"> Entrar </x-ui.button>
    </form>
</div>

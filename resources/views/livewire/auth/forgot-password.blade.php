<div class="flex flex-col gap-8">
    <div class="flex flex-col gap-2 text-center">
        <p class="text-primary text-sm font-semibold tracking-widest uppercase">Recuperação de acesso</p>
        <h1 class="text-2xl font-bold text-gray-900">Esqueci minha senha</h1>
        <p class="text-sm text-gray-600">Informe seu email e enviaremos um link para você criar uma nova senha.</p>
    </div>

    @if (session('status'))
        <x-ui.alert success soft title="{{ session('status') }}" />
    @endif

    <form novalidate wire:submit="sendResetLink" class="flex flex-col gap-5">
        <x-ui.input label="Email" type="email" wire:model.defer="email" required autofocus autocomplete="username" />

        <div class="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
            <x-ui.button link :href="route('admin.login')" sm> Voltar para o login </x-ui.button>

            <x-ui.button primary uppercase type="submit" loading="sendResetLink"> Enviar link </x-ui.button>
        </div>
    </form>
</div>

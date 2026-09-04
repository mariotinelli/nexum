<x-guest-layout>
    <div class="mb-4 text-sm text-gray-600">
        Obrigado por se registrar! Antes de começar, poderia verificar seu endereço de email clicando no link que
        acabamos de enviar? Se você não recebeu o email, ficaremos felizes em enviar outro.
    </div>

    @if (session('status') == 'verification-link-sent')
        <div class="mb-4 text-sm font-medium text-green-600">
            Um novo link de verificação foi enviado para o endereço de email que você forneceu durante o registro.
        </div>
    @endif

    <div class="mt-4 flex items-center justify-between">
        <form method="POST" action="{{ route('verification.send') }}">
            @csrf

            <div>
                <x-ui.button primary sm uppercase> Reenviar Email de Verificação </x-ui.button>
            </div>
        </form>

        <form method="POST" action="{{ route('logout') }}">
            @csrf

            <x-ui.button type="submit" sm link> Sair </x-ui.button>
        </form>
    </div>
</x-guest-layout>

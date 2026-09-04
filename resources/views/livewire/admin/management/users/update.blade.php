<div>
    <x-ui.modal id="update-user-modal" xl :clickAway="false" divided>
        <x-slot name="title">Editar Usuário</x-slot>

        <x-slot name="description">Preencha os campos abaixo para editar um usuário.</x-slot>

        <div class="flex w-full flex-col gap-6">
            <div class="w-full">
                <x-ui.input
                    id="update-user-name"
                    required
                    label="Nome"
                    placeholder="Nome do usuário"
                    wire:model="user.name"
                />
            </div>

            <div class="flex w-full gap-6">
                <div class="min-w-0 flex-1">
                    <x-ui.input
                        id="update-user-email"
                        type="email"
                        required
                        label="E-mail"
                        placeholder="E-mail do usuário"
                        wire:model="user.email"
                    />
                </div>
                <div class="min-w-0 flex-1">
                    <x-ui.input.select-search
                        id="update-user-role"
                        name="user.role_id"
                        label="Perfil"
                        required
                        wire:model.blur="user.role_id"
                        :route="route('search.roles')"
                    />
                </div>
            </div>
        </div>
    </x-ui.modal>
</div>

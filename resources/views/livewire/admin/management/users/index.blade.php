@use('App\Enums\Status')
@use('App\Enums\Permissions\Management\UserPermissions')

<x-ui.page title="Usuários" :breadcrumb="$this->breadcrumb" description="Lista de usuários cadastrados">
    <x-slot name="headerActions">
        @can(UserPermissions::Create)
            <livewire:admin.management.users.create />
        @endcan
    </x-slot>

    <x-ui.table :records="$this->users">
        <x-slot name="filtersDropdown">
            <x-ui.input.multi-select-search
                name="filters.roles"
                label="Perfil"
                wire:model.blur="filters.roles"
                :route="route('search.roles')"
            />

            <x-ui.input.select
                name="filters.status"
                label="Status"
                :options="Status::toArray()"
                :clearable="false"
                wire:model.blur="filters.status"
            />
        </x-slot>

        <x-slot name="header">
            <x-ui.table.th name="name">Nome</x-ui.table.th>
            <x-ui.table.th name="email">E-mail</x-ui.table.th>
            <x-ui.table.th name="role_id">Perfil</x-ui.table.th>
            <x-ui.table.th name="deleted_at">Status</x-ui.table.th>
            <x-ui.table.th>Ações</x-ui.table.th>
        </x-slot>

        <x-slot name="body">
            @forelse ($this->users as $user)
                <x-ui.table.tr wire:key="user-{{ $user->id }}">
                    <x-ui.table.td>{{ $user->name }}</x-ui.table.td>
                    <x-ui.table.td>{{ $user->email }}</x-ui.table.td>
                    <x-ui.table.td>{{ $user->role->name }}</x-ui.table.td>
                    <x-ui.table.td>
                        @if ($user->trashed())
                            <x-ui.badge error>Inativo</x-ui.badge>
                        @else
                            <x-ui.badge success>Ativo</x-ui.badge>
                        @endif
                    </x-ui.table.td>
                    <x-ui.table.td>
                        <div class="flex items-center">
                            @can(UserPermissions::Edit)
                                <x-ui.button
                                    id="edit-user-button-{{ $user->id }}"
                                    class="tooltip table-action"
                                    data-tip="Editar"
                                    ghost
                                    xs
                                    @click="$dispatch('users::update', { userId: {{ $user->id }} })"
                                    wire:target="$dispatch('users::update', { userId: {{ $user->id }} })"
                                >
                                    <x-icons.pencil-square class="text-info size-5!" />
                                </x-ui.button>
                            @endcan
                            @if (!$user->trashed())
                                @can(UserPermissions::Delete)
                                    <x-ui.button
                                        id="delete-user-button-{{ $user->id }}"
                                        class="tooltip table-action"
                                        data-tip="Desativar"
                                        ghost
                                        xs
                                        @click="$dispatch('users::delete', { id: {{ $user->id }} })"
                                        :with-loading="false"
                                    >
                                        <x-icons.x-circle class="text-error size-5!" />
                                    </x-ui.button>
                                @endcan
                            @else
                                @can(UserPermissions::Restore)
                                    <x-ui.button
                                        id="restore-user-button-{{ $user->id }}"
                                        class="tooltip table-action"
                                        data-tip="Ativar"
                                        ghost
                                        xs
                                        @click="$dispatch('users::restore', { id: {{ $user->id }} })"
                                        :with-loading="false"
                                    >
                                        <x-icons.arrow-path class="text-success size-5!" />
                                    </x-ui.button>
                                @endcan
                            @endif
                        </div>
                    </x-ui.table.td>
                </x-ui.table.tr>
            @empty
                <x-ui.table.tr>
                    <x-ui.table.td colspan="5" class="text-center text-gray-500!">
                        Nenhum registro encontrado
                    </x-ui.table.td>
                </x-ui.table.tr>
            @endforelse
        </x-slot>
    </x-ui.table>

    @push('modals')
        <livewire:admin.management.users.delete />
        <livewire:admin.management.users.restore />
        <livewire:admin.management.users.update />
    @endpush
</x-ui.page>

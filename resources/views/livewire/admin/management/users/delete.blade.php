<div>
    <x-ui.modal id="delete-modal" title="Desativar" divided>
        <p class="text-md text-gray-500">Tem certeza que deseja desativar o usuário?</p>

        <x-slot name="footer">
            <div class="flex w-full items-center justify-end gap-2 bg-gray-100 p-3">
                <x-ui.button id="cancel-button" neutral sm wire:click="closeModal">Cancelar</x-ui.button>
                <x-ui.button id="delete-button" error sm wire:click="delete">Desativar</x-ui.button>
            </div>
        </x-slot>
    </x-ui.modal>
</div>

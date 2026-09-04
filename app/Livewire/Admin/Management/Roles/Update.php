<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Management\Roles;

use App\Brain\Roles\Actions\UpdateRoleAction;
use App\Models\Role;
use App\Traits\Components\WithModal;
use App\Traits\Components\WithToast;
use Illuminate\View\View;
use Livewire\Attributes\On;
use Livewire\Component;

class Update extends Component
{
    use WithModal;
    use WithToast;

    public ?Role $role = null;

    public array $selectedPermissions = [];

    public ?int $template = null;

    protected function rules(): array
    {
        return [
            'role.name'             => ['required', 'string', 'min:3', 'max:191'],
            'role.description'      => ['nullable', 'string', 'min:3', 'max:500'],
            'selectedPermissions'   => ['required', 'array'],
            'selectedPermissions.*' => ['required', 'string', 'exists:permissions,name'],
        ];
    }

    public function render(): View
    {
        return view('livewire.admin.management.roles.update');
    }

    public function mount(): void
    {
        $this->role = new Role();
    }

    #[On('roles::update')]
    public function loadRole(int $roleId): void
    {
        $this->role = Role::query()->with('permissions')->findOrFail($roleId);

        $this->authorize('update', $this->role);

        $this->template = null;

        $this->selectedPermissions = $this->role->permissions->pluck('name')->toArray();

        $this->openModal();

        $this->dispatch('select-template', $this->selectedPermissions);
    }

    public function updatedTemplate(?int $templateId): void
    {
        if (!$templateId) {
            $this->selectedPermissions = [];
            $this->dispatch('select-template', $this->selectedPermissions);

            return;
        }

        $this->selectedPermissions = Role::query()
            ->findOrFail($templateId)
            ->permissions
            ->pluck('name')
            ->toArray();

        $this->dispatch('select-template', $this->selectedPermissions);
    }

    public function save(): void
    {
        $this->authorize('update', $this->role);

        $this->validate();

        UpdateRoleAction::dispatchSync([
            'role'     => $this->role,
            'roleData' => [
                'name'        => $this->role->name,
                'description' => $this->role->description,
            ],
            'selectedPermissions' => $this->selectedPermissions,
        ]);

        $this->closeModal();

        $this->toast('Perfil atualizado com sucesso');

        $this->dispatch('roles::refresh');
    }
}

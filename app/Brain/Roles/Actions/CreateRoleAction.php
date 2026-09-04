<?php

declare(strict_types = 1);

namespace App\Brain\Roles\Actions;

use App\Models\Role;
use Brain\Action;

/**
 * @property-read array $roleData
 * @property-read array $selectedPermissions
 * @property Role $role
 */
class CreateRoleAction extends Action
{
    public function rules(): array
    {
        return [
            'roleData.name'         => ['required', 'string', 'min:3', 'max:191'],
            'roleData.description'  => ['nullable', 'string', 'min:3', 'max:500'],
            'selectedPermissions'   => ['required', 'array'],
            'selectedPermissions.*' => ['required', 'string', 'exists:permissions,name'],
        ];
    }

    public function handle(): self
    {
        $this->role = Role::query()->create([
            'name'        => $this->roleData['name'],
            'description' => $this->roleData['description'] ?? null,
        ]);

        $this->role->syncPermissions($this->selectedPermissions);

        return $this;
    }
}

<?php

declare(strict_types = 1);

namespace App\Brain\Users\Actions;

use App\Enums\TypeUsers;
use App\Models\User;
use Brain\Action;
use Illuminate\Validation\Rule;

/**
 * Action UpdateUser
 *
 * @property-read User $user
 * @property-read array $userData
 */
class UpdateUserAction extends Action
{
    public function rules(): array
    {
        return [
            'userData.name'    => ['required', 'string', 'min:3', 'max:191'],
            'userData.email'   => ['required', 'email', 'max:191', Rule::unique('users', 'email')->ignore($this->user->id)],
            'userData.type'    => ['required', Rule::enum(TypeUsers::class)],
            'userData.role_id' => ['nullable', 'exists:roles,id'],
        ];
    }

    public function handle(): self
    {
        $this->user->update([
            'name'    => $this->userData['name'],
            'email'   => $this->userData['email'],
            'type'    => $this->userData['type'],
            'role_id' => $this->userData['role_id'] ?? $this->user->role_id,
        ]);

        return $this;
    }
}

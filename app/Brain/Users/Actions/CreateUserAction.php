<?php

declare(strict_types = 1);

namespace App\Brain\Users\Actions;

use App\Enums\TypeUsers;
use App\Models\User;
use Brain\Action;
use Brain\Attributes\Sensitive;
use Illuminate\Validation\Rule;

/**
 * Action CreateUser
 *
 * @property-read array $userData
 * @property-read string $password
 *
 * @property User $user
 */
#[Sensitive('password')]
class CreateUserAction extends Action
{
    public function rules(): array
    {
        return [
            'userData.name'    => ['required', 'string', 'min:3', 'max:191'],
            'userData.email'   => ['required', 'email', 'max:191', 'unique:users,email'],
            'userData.type'    => ['required', Rule::enum(TypeUsers::class)],
            'userData.role_id' => ['nullable', 'exists:roles,id'],
            'password'         => ['required', 'string', 'min:8', 'max:191'],
        ];
    }

    public function handle(): self
    {
        $this->user = User::query()->create([
            'name'     => $this->userData['name'],
            'email'    => $this->userData['email'],
            'type'     => $this->userData['type'],
            'role_id'  => $this->userData['role_id'] ?? null,
            'password' => $this->password,
        ]);

        return $this;
    }
}

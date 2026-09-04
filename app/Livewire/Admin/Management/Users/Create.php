<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Management\Users;

use App\Brain\Users\Actions\CreateUserAction;
use App\Enums\TypeUsers;
use App\Models\User;
use App\Notifications\NewUserNotification;
use App\Traits\Components\WithModal;
use App\Traits\Components\WithToast;
use Illuminate\Support\Str;
use Illuminate\View\View;
use Livewire\Component;

class Create extends Component
{
    use WithModal;
    use WithToast;

    public ?User $user = null;

    public function render(): View
    {
        return view('livewire.admin.management.users.create');
    }

    public function rules(): array
    {
        return [
            'user.name'    => ['required', 'string', 'min:3', 'max:191'],
            'user.email'   => ['required', 'email', 'unique:users,email', 'max:191'],
            'user.role_id' => ['required', 'exists:roles,id'],
        ];
    }

    public function mount(): void
    {
        $this->user = new User();
    }

    public function loadUser(): void
    {
        $this->authorize('create', User::class);

        $this->user = new User();

        $this->openModal();
    }

    public function save(): void
    {
        $this->authorize('create', User::class);

        $this->validate();

        $password = Str::random(8);

        /** @var CreateUserAction $task */
        $task = CreateUserAction::dispatchSync([
            'userData' => $this->user->toArray() + [
                'type'    => TypeUsers::User,
                'role_id' => $this->user->role_id,
            ],
            'password' => $password,
        ]);

        $task->user->notify(new NewUserNotification($password));

        $this->closeModal();

        $this->toast('Usuário cadastrado com sucesso');

        $this->dispatch('users::refresh');
    }
}

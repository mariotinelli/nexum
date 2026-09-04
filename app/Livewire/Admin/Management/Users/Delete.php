<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Management\Users;

use App\Brain\Users\Actions\DeleteUserAction;
use App\Models\User;
use App\Traits\Components\WithModal;
use App\Traits\Components\WithToast;
use Illuminate\View\View;
use Livewire\Attributes\On;
use Livewire\Component;

class Delete extends Component
{
    use WithModal;
    use WithToast;

    public ?User $user = null;

    public function render(): View
    {
        return view('livewire.admin.management.users.delete');
    }

    #[On('users::delete')]
    public function loadUser(int $id): void
    {
        $this->user = User::findOrFail($id);

        $this->authorize('delete', $this->user);

        $this->openModal();
    }

    public function delete(): void
    {
        $this->authorize('delete', $this->user);

        DeleteUserAction::dispatchSync([
            'user' => $this->user,
        ]);

        $this->closeModal();

        $this->toast('Usuário desativado com sucesso');

        $this->dispatch('users::refresh');
    }
}

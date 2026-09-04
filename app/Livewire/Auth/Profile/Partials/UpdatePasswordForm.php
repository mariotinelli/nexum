<?php

declare(strict_types = 1);

namespace App\Livewire\Auth\Profile\Partials;

use App\Traits\Components\WithToast;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;
use Illuminate\View\View;
use Livewire\Component;

class UpdatePasswordForm extends Component
{
    use WithToast;

    public string $current_password = '';

    public string $password = '';

    public string $password_confirmation = '';

    public function render(): View
    {
        return view('livewire.auth.profile.partials.update-password-form');
    }

    public function updatePassword(): void
    {
        $this->validatePassword();

        Auth::user()->update([
            'password' => Hash::make($this->password),
        ]);

        $this->reset(['current_password', 'password', 'password_confirmation']);

        $this->toast('Senha atualizada com sucesso!');
    }

    private function validatePassword(): void
    {
        $this->validate([
            'current_password' => ['required', 'string'],
            'password'         => ['required', 'string', 'min:8', 'confirmed'],
        ]);

        if (!Hash::check($this->current_password, Auth::user()->password)) {

            throw ValidationException::withMessages([
                'current_password' => ['A senha atual está incorreta.'],
            ]);

        }
    }
}

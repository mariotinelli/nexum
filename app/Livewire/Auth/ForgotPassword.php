<?php

declare(strict_types = 1);

namespace App\Livewire\Auth;

use Illuminate\Support\Facades\Password;
use Illuminate\View\View;
use Livewire\Attributes\Layout;
use Livewire\Component;

#[Layout('layouts.guest', ['variant' => 'split'])]
class ForgotPassword extends Component
{
    public string $email = '';

    public function rules(): array
    {
        return [
            'email' => ['required', 'email'],
        ];
    }

    public function render(): View
    {
        return view('livewire.auth.forgot-password');
    }

    public function sendResetLink(): void
    {
        $this->validate();

        $status = Password::sendResetLink([
            'email' => $this->email,
        ]);

        if ($status === Password::INVALID_USER) {
            session()->flash('status', __(Password::RESET_LINK_SENT));

            return;
        }

        if ($status !== Password::RESET_LINK_SENT) {
            $this->addError('email', __($status));

            return;
        }

        session()->flash('status', __($status));
    }
}

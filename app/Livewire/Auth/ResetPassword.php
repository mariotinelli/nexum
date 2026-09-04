<?php

declare(strict_types = 1);

namespace App\Livewire\Auth;

use App\Models\User;
use App\Traits\Components\WithToast;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Http\RedirectResponse;
use Illuminate\Routing\Redirector;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;
use Illuminate\Validation\Rules;
use Illuminate\View\View;
use Livewire\Attributes\Layout;
use Livewire\Component;

#[Layout('layouts.guest', ['variant' => 'split'])]
class ResetPassword extends Component
{
    use WithToast;

    public string $token = '';

    public string $email = '';

    public string $password = '';

    public string $password_confirmation = '';

    public function rules(): array
    {
        return [
            'token'    => ['required'],
            'email'    => ['required', 'email'],
            'password' => ['required', 'confirmed', Rules\Password::defaults()],
        ];
    }

    public function render(): View
    {
        return view('livewire.auth.reset-password');
    }

    public function mount(string $token): void
    {
        $this->token = $token;
        $this->email = (string) request()->get('email', '');
    }

    public function save(): RedirectResponse | Redirector | null
    {
        $this->validate();

        $status = Password::reset(
            [
                'email'                 => $this->email,
                'password'              => $this->password,
                'password_confirmation' => $this->password_confirmation,
                'token'                 => $this->token,
            ],
            function (User $user, string $password): void {
                $user->forceFill([
                    'password'       => Hash::make($password),
                    'remember_token' => Str::random(60),
                ])->save();

                event(new PasswordReset($user));
            }
        );

        if ($status === Password::PASSWORD_RESET) {
            $this->toast('Senha resetada com sucesso', nextPage: true);

            return redirect()->route('admin.login');
        }

        $this->addError('email', __($status));

        return null;
    }
}

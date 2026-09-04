<?php

declare(strict_types = 1);

namespace App\Livewire\Auth\Profile\Partials;

use App\Traits\Components\WithToast;
use Illuminate\Validation\Rule;
use Illuminate\View\View;
use Livewire\Component;

class UpdateProfileInformationForm extends Component
{
    use WithToast;

    public string $name = '';

    public string $email = '';

    protected function rules(): array
    {
        return [
            'name'  => ['required', 'string', 'max:191'],
            'email' => ['required', 'email', 'max:191', Rule::unique('users')->ignore(auth()->id())],
        ];
    }

    public function render(): View
    {
        return view('livewire.auth.profile.partials.update-profile-information-form');
    }

    public function mount(): void
    {
        $this->name  = user()->name;
        $this->email = user()->email;
    }

    public function save(): void
    {
        $this->validate();

        user()->name  = $this->name;
        user()->email = $this->email;

        user()->save();

        $this->toast('Perfil atualizado com sucesso!');
    }
}

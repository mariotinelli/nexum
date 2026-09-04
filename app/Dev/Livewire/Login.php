<?php

declare(strict_types = 1);

namespace App\Dev\Livewire;

use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Response;
use Livewire\Attributes\Computed;
use Livewire\Component;
use Livewire\Features\SupportRedirects\Redirector;

/**
 * @property-read Collection $users
 */
class Login extends Component
{
    private const string HOME = 'home';

    public ?int $selectedUser = null;

    public function mount(): void
    {
        $this->selectedUser = user()?->id;
    }

    public function render(): string
    {
        return <<<'BLADE'
            <div class="join h-10">
                <select name="name" wire:model="selectedUser" class="select select-primary join-item">
                    <option value="0" selected></option>
                    @foreach($this->users as $user)
                        <option value="{{ $user->id }}">
                            {{ $user->formatted_name . ' (' . $user->type->label() . ')' }}
                        </option>
                    @endforeach
                </select>
                <x-ui.button sm primary wire:click="login" class="font-bold join-item h-10">
                    LOGIN
                </x-ui.button>
            </div>
        BLADE;
    }

    #[Computed]
    public function users(): Collection
    {
        return User::query()
            // ->with('customer')
            ->get();
    }

    public function login(): Redirector | RedirectResponse
    {
        abort_if(!withEnvBar(), Response::HTTP_UNAUTHORIZED);

        $this->validate(['selectedUser' => 'required']);

        session()->put('fake_login', true);

        auth()->loginUsingId($this->selectedUser);

        return redirect()->route(self::HOME);
    }
}

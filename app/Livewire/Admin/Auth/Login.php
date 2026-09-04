<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Auth;

use App\Enums\TypeUsers;
use Illuminate\Auth\Events\Lockout;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;
use Illuminate\View\View;
use Livewire\Attributes\Layout;
use Livewire\Component;
use Livewire\Features\SupportRedirects\Redirector as LivewireRedirector;

#[Layout('layouts.guest', ['variant' => 'split'])]
class Login extends Component
{
    public string $email = '';

    public string $password = '';

    public bool $remember = false;

    public function render(): View
    {
        return view('livewire.auth.login');
    }

    public function rules(): array
    {
        return [
            'email'    => ['required', 'email'],
            'password' => ['required', 'string'],
        ];
    }

    public function login(): RedirectResponse | LivewireRedirector
    {
        $data = $this->validate();

        $this->ensureIsNotRateLimited();

        if (!Auth::attempt([
            'email'    => $data['email'],
            'password' => $data['password'],
            static fn (Builder $query): Builder => $query->whereIn('type', TypeUsers::adminAreaValues()),
        ], $this->remember)) {
            RateLimiter::hit($this->throttleKey());

            throw ValidationException::withMessages([
                'email' => __('auth.failed'),
            ]);
        }

        RateLimiter::clear($this->throttleKey());

        session()->regenerate();

        return $this->redirectToIntendedAdminPage();
    }

    public function ensureIsNotRateLimited(): void
    {
        if (!RateLimiter::tooManyAttempts($this->throttleKey(), 5)) {
            return;
        }

        event(new Lockout(request()));

        $seconds = RateLimiter::availableIn($this->throttleKey());

        throw ValidationException::withMessages([
            'email' => __('auth.throttle', [
                'seconds' => $seconds,
                'minutes' => (int) ceil($seconds / 60),
            ]),
        ]);
    }

    public function throttleKey(): string
    {
        return Str::transliterate(Str::lower($this->email)) . '|' . request()->ip();
    }

    // @phpstan-ignore return.unusedType (Livewire replaces Laravel's redirector binding at runtime.)
    private function redirectToIntendedAdminPage(): RedirectResponse | LivewireRedirector
    {
        $adminUrl    = route('admin.dashboard');
        $intendedUrl = session()->pull('url.intended');

        if (is_string($intendedUrl) && $this->isAdminUrl($intendedUrl, $adminUrl)) {
            return redirect()->to($intendedUrl);
        }

        return redirect()->route('admin.dashboard');
    }

    private function isAdminUrl(string $intendedUrl, string $adminUrl): bool
    {
        return $intendedUrl === $adminUrl
            || Str::startsWith($intendedUrl, $adminUrl . '/')
            || Str::startsWith($intendedUrl, $adminUrl . '?');
    }
}

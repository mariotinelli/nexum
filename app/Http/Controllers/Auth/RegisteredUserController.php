<?php

declare(strict_types = 1);

namespace App\Http\Controllers\Auth;

use App\Brain\Users\Actions\CreateUserAction;
use App\Enums\TypeUsers;
use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Auth\Events\Registered;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\Rules;
use Illuminate\View\View;

class RegisteredUserController extends Controller
{
    public function create(): View
    {
        return view('auth.register');
    }

    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'name'     => ['required', 'string', 'max:191'],
            'email'    => ['required', 'string', 'lowercase', 'email', 'max:191', 'unique:' . User::class],
            'password' => ['required', 'confirmed', Rules\Password::defaults()],
        ]);

        /** @var CreateUserAction $task */
        $task = CreateUserAction::dispatchSync([
            'userData' => [
                'name'  => $validated['name'],
                'email' => $validated['email'],
                'type'  => TypeUsers::Customer,
            ],
            'password' => $validated['password'],
        ]);

        event(new Registered($task->user));

        Auth::login($task->user);

        return redirect(route('dashboard', absolute: false));
    }
}

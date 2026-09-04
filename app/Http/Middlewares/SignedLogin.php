<?php

declare(strict_types = 1);

namespace App\Http\Middlewares;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class SignedLogin
{
    public function handle(Request $request, Closure $next): Response
    {
        $userId = request()->query('user');

        abort_if(blank($userId), Response::HTTP_FORBIDDEN);

        if (user()?->id !== (int) $userId) {
            session()->put('fake_login', true);
            auth()->loginUsingId($userId);
        }

        return $next($request);
    }
}

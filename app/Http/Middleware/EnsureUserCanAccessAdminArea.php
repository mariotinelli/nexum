<?php

declare(strict_types = 1);

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserCanAccessAdminArea
{
    public function handle(Request $request, Closure $next): Response
    {
        $user = $request->user();

        if ($user === null || !$user->type->canAccessAdminArea()) {
            abort(403, 'Acesso não autorizado.');
        }

        return $next($request);
    }
}

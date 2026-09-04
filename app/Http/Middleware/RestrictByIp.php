<?php

declare(strict_types = 1);

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class RestrictByIp
{
    public function handle(Request $request, Closure $next): Response
    {
        /** @var array<int, string> $allowedIps */
        $allowedIps = config('artisan-executor.allowed_ips', []);

        if ($allowedIps === []) {
            return $next($request);
        }

        $clientIp = $request->ip();

        if ($clientIp === null || !in_array($clientIp, $allowedIps, true)) {
            abort(403, 'Seu IP não está autorizado para usar o executor de comandos.');
        }

        return $next($request);
    }
}

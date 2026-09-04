<?php

declare(strict_types = 1);

use App\Models\User;
use App\Support\Alerts\DiscordAlert;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__ . '/../routes/web.php',
        commands: __DIR__ . '/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->redirectGuestsTo(fn (Request $request): string => route('admin.login'));

        $middleware->redirectUsersTo(function (Request $request): string {
            $user = $request->user();

            return $user instanceof User && $user->type->canAccessAdminArea()
                ? route('admin.dashboard')
                : route('dashboard');
        });
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->dontReportDuplicates();

        $exceptions->report(function (Throwable $throwable): void {
            app(DiscordAlert::class)->report($throwable);
        });
    })->create();

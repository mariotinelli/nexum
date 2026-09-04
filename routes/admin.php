<?php

declare(strict_types = 1);

use App\Http\Middleware\EnsureUserCanAccessAdminArea;
use App\Http\Middleware\RestrictByIp;
use App\Livewire\Admin\Auth\Login;
use App\Livewire\Admin\Management;
use App\Livewire\Admin\Support;
use App\Livewire\Admin\Support\ArtisanCommands;
use App\Models\CommandExecution;
use App\Models\Role;
use App\Models\SystemErrorAlert;
use App\Models\User;
use Illuminate\Support\Facades\Route;

Route::prefix('admin')
    ->as('admin.')
    ->group(function (): void {
        Route::middleware('guest')->group(function (): void {
            Route::livewire('login', Login::class)->name('login');
        });

        Route::middleware(['auth', EnsureUserCanAccessAdminArea::class])->group(function (): void {
            Route::get('/dashboard', fn () => view('dashboard'))->middleware(['auth'])->name('dashboard');

            Route::prefix('gestao')
                ->as('management.')
                ->group(function (): void {
                    Route::prefix('perfis')
                        ->as('roles.')
                        ->group(function (): void {
                            Route::livewire('/', Management\Roles\Index::class)
                                ->can('view-any', Role::class)
                                ->name('index');
                        });

                    Route::prefix('usuarios')
                        ->as('users.')
                        ->group(function (): void {
                            Route::livewire('/', Management\Users\Index::class)
                                ->can('view-any', User::class)
                                ->name('index');
                        });
                });

            Route::prefix('suporte-rem-soft')
                ->as('support.')
                ->group(function (): void {
                    Route::prefix('alertas-erros')
                        ->as('system-error-alerts.')
                        ->group(function (): void {
                            Route::livewire('/', Support\SystemErrorAlerts\Index::class)
                                ->can('view-any', SystemErrorAlert::class)
                                ->name('index');

                            Route::livewire('{systemErrorAlert}', Support\SystemErrorAlerts\Show::class)
                                ->can('view', 'systemErrorAlert')
                                ->name('show');
                        });

                    Route::prefix('executor-artisan')
                        ->middleware(RestrictByIp::class)
                        ->as('artisan-commands.')
                        ->group(function (): void {
                            Route::livewire('/', ArtisanCommands\Index::class)
                                ->can('view-any', CommandExecution::class)
                                ->name('index');
                        });
                });
        });
    });

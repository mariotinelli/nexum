<?php

declare(strict_types = 1);

use App\Livewire\Auth\Profile\EditProfile;
use Illuminate\Support\Facades\Route;

Route::get('/', fn () => to_route('dashboard'))->name('home');

Route::get('/dashboard', fn () => view('dashboard'))->middleware(['auth'])->name('dashboard');

Route::middleware(['auth'])->group(function (): void {
    Route::livewire('/perfil', EditProfile::class)->name('profile.edit');
});

require __DIR__ . '/auth.php';

require __DIR__ . '/search.php';

require __DIR__ . '/admin.php';

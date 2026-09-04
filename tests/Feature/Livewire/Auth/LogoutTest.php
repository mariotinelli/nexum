<?php

declare(strict_types = 1);

use App\Livewire\Auth\Logout;
use App\Models\User;

use function Pest\Laravel\actingAs;
use function Pest\Livewire\livewire;

it('logs out authenticated admin and redirects to login', function (): void {
    /** @var User $user */
    $user = User::factory()->admin()->create();
    actingAs($user);

    livewire(Logout::class)
        ->call('logout')
        ->assertRedirect(route('admin.login'));

    expect(auth()->check())->toBeFalse();
});

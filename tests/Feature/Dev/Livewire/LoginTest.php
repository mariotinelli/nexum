<?php

declare(strict_types = 1);

use App\Dev\Livewire\Login;
use App\Models\User;

use Illuminate\Support\Collection;

use function Pest\Livewire\livewire;

beforeEach(function (): void {
    $this->users = User::factory(10)->create();
});

it('should be list all users', function (): void {
    livewire(Login::class)
        ->assertSet('users', fn (Collection $users): bool => $users->count() === 10);
});

it('can be able to login with the selected user', function (): void {
    livewire(Login::class)
        ->set('selectedUser', $this->users->first()->id)
        ->call('login')
        ->assertRedirectToRoute('home');

    expect(session('fake_login'))->toBeTrue()
        ->and(auth()->id())->toBe($this->users->first()->id);
});

it('can not be able to login with has not selected user', function (): void {
    livewire(Login::class)
        ->set('selectedUser', null)
        ->call('login')
        ->assertHasErrors('selectedUser');

    expect(session('fake_login'))->toBeNull()
        ->and(auth()->id())->toBeNull();
});

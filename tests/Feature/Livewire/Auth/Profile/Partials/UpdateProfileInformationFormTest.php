<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Livewire\Auth\Profile\Partials\UpdateProfileInformationForm;
use App\Models\User;

use function Pest\Laravel\actingAs;
use function Pest\Livewire\livewire;

it('mounts with authenticated user data and updates profile information', function (): void {
    /** @var User $user */
    $user = User::factory()->create([
        'type'  => TypeUsers::User,
        'name'  => 'Old Name',
        'email' => 'old@example.com',
    ]);

    actingAs($user);

    livewire(UpdateProfileInformationForm::class)
        ->assertSet('name', 'Old Name')
        ->assertSet('email', 'old@example.com')
        ->set('name', 'New Name')
        ->set('email', 'new@example.com')
        ->call('save')
        ->assertDispatched('toast');

    expect($user->fresh()->name)->toBe('New Name')
        ->and($user->fresh()->email)->toBe('new@example.com');
});

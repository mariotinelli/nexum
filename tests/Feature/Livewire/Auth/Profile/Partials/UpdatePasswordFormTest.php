<?php

declare(strict_types = 1);

use App\Livewire\Auth\Profile\Partials\UpdatePasswordForm;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

use function Pest\Laravel\actingAs;
use function Pest\Livewire\livewire;

it('updates password with correct current password', function (): void {
    /** @var User $user */
    $user = User::factory()->create([
        'password' => Hash::make('OldPass@123'),
    ]);

    actingAs($user);

    livewire(UpdatePasswordForm::class)
        ->set('current_password', 'OldPass@123')
        ->set('password', 'NewPass@123')
        ->set('password_confirmation', 'NewPass@123')
        ->call('updatePassword')
        ->assertDispatched('toast')
        ->assertSet('current_password', '')
        ->assertSet('password', '')
        ->assertSet('password_confirmation', '');

    expect(Hash::check('NewPass@123', $user->fresh()->password))->toBeTrue();
});

it('throws validation error when current password is invalid', function (): void {
    /** @var User $user */
    $user = User::factory()->create([
        'password' => Hash::make('OldPass@123'),
    ]);

    actingAs($user);

    livewire(UpdatePasswordForm::class)
        ->set('current_password', 'WrongPass')
        ->set('password', 'NewPass@123')
        ->set('password_confirmation', 'NewPass@123')
        ->call('updatePassword')
        ->assertHasErrors('current_password');
});

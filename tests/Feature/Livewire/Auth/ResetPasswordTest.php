<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Livewire\Auth\ResetPassword;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;

use function Pest\Livewire\livewire;

it('mounts the reset token and email', function (): void {
    livewire(ResetPassword::class, ['token' => 'reset-token'])
        ->assertSet('token', 'reset-token')
        ->assertSet('email', '');
});

it('validates reset password data', function (): void {
    livewire(ResetPassword::class, ['token' => ''])
        ->call('save')
        ->assertHasErrors([
            'token'    => 'required',
            'email'    => 'required',
            'password' => 'required',
        ]);
});

it('resets passwords for user types allowed in the admin area', function (TypeUsers $type): void {
    $user  = User::factory()->create(['type' => $type]);
    $token = Password::createToken($user);

    livewire(ResetPassword::class, ['token' => $token])
        ->set('email', $user->email)
        ->set('password', 'NewSecure@123456')
        ->set('password_confirmation', 'NewSecure@123456')
        ->call('save')
        ->assertHasNoErrors()
        ->assertRedirect(route('admin.login'));

    expect(Hash::check('NewSecure@123456', $user->fresh()->password))->toBeTrue();
})->with([
    'admin'   => TypeUsers::Admin,
    'user'    => TypeUsers::User,
    'support' => TypeUsers::SupportRemSoft,
]);

it('resets a customer password with a valid token', function (): void {
    $customer = User::factory()->customer()->create();
    $token    = Password::createToken($customer);

    livewire(ResetPassword::class, ['token' => $token])
        ->set('email', $customer->email)
        ->set('password', 'NewSecure@123456')
        ->set('password_confirmation', 'NewSecure@123456')
        ->call('save')
        ->assertHasNoErrors()
        ->assertRedirect(route('admin.login'));

    expect(Hash::check('NewSecure@123456', $customer->fresh()->password))->toBeTrue();
});

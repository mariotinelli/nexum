<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Livewire\Auth\ForgotPassword;
use App\Models\User;
use Illuminate\Auth\Notifications\ResetPassword;
use Illuminate\Support\Facades\Notification;
use Illuminate\Support\Facades\Password;

use function Pest\Livewire\livewire;

it('validates email before sending reset link', function (): void {
    livewire(ForgotPassword::class)
        ->set('email', '')
        ->call('sendResetLink')
        ->assertHasErrors(['email' => 'required']);
});

it('flashes status when password reset link is sent', function (): void {
    $user = User::factory()->admin()->create();

    Password::shouldReceive('sendResetLink')
        ->once()
        ->with(['email' => $user->email])
        ->andReturn(Password::RESET_LINK_SENT);

    livewire(ForgotPassword::class)
        ->set('email', $user->email)
        ->call('sendResetLink')
        ->assertHasNoErrors()
        ->assertSee(__(Password::RESET_LINK_SENT));
});

it('adds email error when reset link cannot be sent', function (): void {
    $user = User::factory()->admin()->create();

    Password::shouldReceive('sendResetLink')
        ->once()
        ->andReturn(Password::RESET_THROTTLED);

    livewire(ForgotPassword::class)
        ->set('email', $user->email)
        ->call('sendResetLink')
        ->assertHasErrors('email');
});

it('sends the shared password reset URL to every user type', function (TypeUsers $type): void {
    Notification::fake();

    $user = User::factory()->create(['type' => $type]);

    livewire(ForgotPassword::class)
        ->set('email', $user->email)
        ->call('sendResetLink')
        ->assertHasNoErrors();

    Notification::assertSentTo(
        $user,
        ResetPassword::class,
        fn (ResetPassword $notification): bool => str_contains(
            $notification->toMail($user)->actionUrl,
            '/nova-senha/',
        ),
    );
})->with([
    'admin'    => TypeUsers::Admin,
    'user'     => TypeUsers::User,
    'customer' => TypeUsers::Customer,
    'support'  => TypeUsers::SupportRemSoft,
]);

it('does not reveal or notify unknown emails', function (): void {
    Notification::fake();

    livewire(ForgotPassword::class)
        ->set('email', 'unknown@example.com')
        ->call('sendResetLink')
        ->assertHasNoErrors()
        ->assertSee(__(Password::RESET_LINK_SENT));

    Notification::assertNothingSent();
});

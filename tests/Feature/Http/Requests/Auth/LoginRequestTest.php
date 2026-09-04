<?php

declare(strict_types = 1);

use App\Http\Requests\Auth\LoginRequest;
use Illuminate\Auth\Events\Lockout;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Validation\ValidationException;

it('returns authorization and validation rules', function (): void {
    $request = LoginRequest::create('/login', 'POST');

    expect($request->authorize())->toBeTrue()
        ->and($request->rules())->toBe([
            'email'    => ['required', 'string', 'email'],
            'password' => ['required', 'string'],
        ]);
});

it('authenticates and clears rate limiter on success', function (): void {
    $request = LoginRequest::create('/login', 'POST', [
        'email'    => 'user@example.com',
        'password' => 'secret',
        'remember' => '1',
    ]);

    RateLimiter::shouldReceive('tooManyAttempts')->once()->andReturnFalse();
    Auth::shouldReceive('attempt')->once()->andReturnTrue();
    RateLimiter::shouldReceive('clear')->once();

    $request->authenticate();

    expect(true)->toBeTrue();
});

it('throws validation exception and hits rate limiter on failed authentication', function (): void {
    $request = LoginRequest::create('/login', 'POST', [
        'email'    => 'user@example.com',
        'password' => 'wrong',
    ]);

    RateLimiter::shouldReceive('tooManyAttempts')->once()->andReturnFalse();
    Auth::shouldReceive('attempt')->once()->andReturnFalse();
    RateLimiter::shouldReceive('hit')->once();

    expect(fn () => $request->authenticate())
        ->toThrow(ValidationException::class);
});

it('throws lockout validation exception when too many attempts', function (): void {
    Event::fake([Lockout::class]);

    $request = LoginRequest::create('/login', 'POST', [
        'email' => 'user@example.com',
    ]);

    RateLimiter::shouldReceive('tooManyAttempts')->once()->andReturnTrue();
    RateLimiter::shouldReceive('availableIn')->once()->andReturn(120);

    expect(fn () => $request->ensureIsNotRateLimited())
        ->toThrow(ValidationException::class);

    Event::assertDispatched(Lockout::class);
});

it('builds throttle key from lowercased transliterated email and ip', function (): void {
    $request = LoginRequest::create('/login', 'POST', [
        'email' => 'Tést@Example.COM',
    ], [], [], ['REMOTE_ADDR' => '127.0.0.1']);

    expect($request->throttleKey())->toBe('test@example.com|127.0.0.1');
});

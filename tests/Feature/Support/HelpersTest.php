<?php

declare(strict_types = 1);

use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cookie;

use function Pest\Laravel\actingAs;

it('returns current authenticated user and null when guest', function (): void {
    expect(user())->toBeNull();

    /** @var User $authUser */
    $authUser = User::factory()->create();
    actingAs($authUser);

    expect(user())->toBeInstanceOf(User::class)
        ->and(user()?->id)->toBe($authUser->id);
});

it('resolves env bar visibility based on environment and qa cookie flag', function (): void {
    app()->detectEnvironment(fn (): string => 'production');

    expect(withEnvBar())->toBeFalse();

    app()->detectEnvironment(fn (): string => 'qa');
    request()->cookies->set('qa_envbar_enabled', '1');

    expect(withEnvBar())->toBeTrue();

    app()->detectEnvironment(fn (): string => 'testing');
});

it('queues env bar cookie on login only in qa', function (): void {
    $user = User::factory()->create();

    app()->detectEnvironment(fn (): string => 'production');
    Auth::login($user);

    expect(collect(Cookie::getQueuedCookies())->contains(
        fn (Symfony\Component\HttpFoundation\Cookie $cookie): bool => $cookie->getName() === 'qa_envbar_enabled',
    ))->toBeFalse();

    app()->detectEnvironment(fn (): string => 'qa');
    Auth::logout();
    Auth::login($user);

    expect(collect(Cookie::getQueuedCookies())->contains(
        fn (Symfony\Component\HttpFoundation\Cookie $cookie): bool => $cookie->getName() === 'qa_envbar_enabled',
    ))->toBeTrue();

    app()->detectEnvironment(fn (): string => 'testing');
});

it('returns default statuses and compares money values', function (): void {
    expect(defaultStatuses())->toBe([1 => 'Ativo', 0 => 'Inativo'])
        ->and(compareMoney('1,00', '1,00'))->toBeFalse()
        ->and(compareMoney('1,00', '2,00'))->toBeTrue()
        ->and(compareMoney('1,00', '1,00', '==='))->toBeTrue();
});

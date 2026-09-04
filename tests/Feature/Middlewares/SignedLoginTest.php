<?php

declare(strict_types = 1);

use App\Http\Middlewares\SignedLogin as HttpSignedLogin;
use App\Middlewares\SignedLogin as BaseSignedLogin;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

use function Pest\Laravel\actingAs;

use Symfony\Component\HttpFoundation\Response;

use Symfony\Component\HttpKernel\Exception\HttpException;

it('aborts with forbidden when user query is missing', function (): void {
    $request = Request::create('/signed-login', 'GET');
    app()->instance('request', $request);

    $middleware = new HttpSignedLogin();

    expect(fn () => $middleware->handle($request, fn () => response('ok')))
        ->toThrow(HttpException::class);
});

it('logs user and sets fake login session when ids differ', function (): void {
    /** @var User $loggedUser */
    $loggedUser = User::factory()->create();
    /** @var User $targetUser */
    $targetUser = User::factory()->create();

    actingAs($loggedUser);

    $request = Request::create('/signed-login?user=' . $targetUser->id, 'GET');
    app()->instance('request', $request);

    $response = (new HttpSignedLogin())->handle($request, fn (): Response => response('ok'));

    expect($response->getContent())->toBe('ok')
        ->and(session('fake_login'))->toBeTrue()
        ->and(Auth::id())->toBe($targetUser->id);
});

it('keeps current auth when user query matches current user', function (): void {
    /** @var User $user */
    $user = User::factory()->create();
    actingAs($user);

    $request = Request::create('/signed-login?user=' . $user->id, 'GET');
    app()->instance('request', $request);

    $response = (new BaseSignedLogin())->handle($request, fn (): Response => response('ok'));

    expect($response->getContent())->toBe('ok')
        ->and(session('fake_login'))->toBeNull()
        ->and(Auth::id())->toBe($user->id);
});

it('aborts on base middleware when user query is missing', function (): void {
    $request = Request::create('/signed-login', 'GET');
    app()->instance('request', $request);

    $middleware = new BaseSignedLogin();

    expect(fn () => $middleware->handle($request, fn () => response('ok')))
        ->toThrow(HttpException::class);
});

it('logs target user on base middleware when ids differ', function (): void {
    /** @var User $loggedUser */
    $loggedUser = User::factory()->create();
    /** @var User $targetUser */
    $targetUser = User::factory()->create();

    actingAs($loggedUser);

    $request = Request::create('/signed-login?user=' . $targetUser->id, 'GET');
    app()->instance('request', $request);

    $response = (new BaseSignedLogin())->handle($request, fn (): Response => response('ok'));

    expect($response->getContent())->toBe('ok')
        ->and(session('fake_login'))->toBeTrue()
        ->and(Auth::id())->toBe($targetUser->id);
});

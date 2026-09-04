<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Models\User;

use function Pest\Laravel\actingAs;
use function Pest\Laravel\get;

it('renders the admin login and redirects the legacy login URL', function (): void {
    get('/admin/login')->assertSuccessful();
    get('/login')->assertRedirect('/admin/login');
});

it('redirects guests from the admin area to the admin login', function (): void {
    get('/admin/dashboard')->assertRedirect(route('admin.login'));
});

it('allows authenticated admin area user types', function (TypeUsers $type): void {
    actingAs(User::factory()->create(['type' => $type]));

    get('/admin/dashboard')->assertSuccessful();
})->with([
    'admin'   => TypeUsers::Admin,
    'user'    => TypeUsers::User,
    'support' => TypeUsers::SupportRemSoft,
]);

it('forbids authenticated customers from the admin area', function (): void {
    actingAs(User::factory()->customer()->create());

    get('/admin/dashboard')->assertForbidden();
});

it('redirects authenticated users away from the admin login according to their access', function (): void {
    actingAs(User::factory()->admin()->create());
    get('/admin/login')->assertRedirect(route('admin.dashboard'));

    auth()->logout();

    actingAs(User::factory()->customer()->create());
    get('/admin/login')->assertRedirect(route('dashboard'));
});

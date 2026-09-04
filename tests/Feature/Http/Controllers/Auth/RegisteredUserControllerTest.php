<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Models\User;
use Illuminate\Auth\Events\Registered;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Hash;

use function Pest\Laravel\post;

it('registers and authenticates a customer through the reusable create user action', function (): void {
    Event::fake([Registered::class]);

    $response = post('/register', [
        'name'                  => 'Cliente Exemplo',
        'email'                 => 'cliente@example.com',
        'password'              => 'CustomerSecure@123456',
        'password_confirmation' => 'CustomerSecure@123456',
    ]);

    $customer = User::query()->where('email', 'cliente@example.com')->firstOrFail();

    $response->assertRedirect('/dashboard');

    expect($customer->type)->toBe(TypeUsers::Customer)
        ->and(Hash::check('CustomerSecure@123456', $customer->password))->toBeTrue()
        ->and(auth()->id())->toBe($customer->id);

    Event::assertDispatched(Registered::class, fn (Registered $event): bool => $event->user->is($customer));
});

it('validates public registration data', function (): void {
    post('/register', [
        'name'                  => '',
        'email'                 => 'invalid-email',
        'password'              => 'weak',
        'password_confirmation' => 'different',
    ])->assertSessionHasErrors(['name', 'email', 'password']);

    expect(User::query()->count())->toBe(0);
});

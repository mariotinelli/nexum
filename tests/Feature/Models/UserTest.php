<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Models\User;

it('returns initials accessor using first two characters uppercase', function (): void {
    $user = User::factory()->create([
        'name' => 'maria silva',
    ]);

    expect($user->initials)->toBe('MA');
});

it('returns formatted name accessor', function (): void {
    $user = User::factory()->create([
        'name' => 'Joao Souza',
    ]);

    expect($user->formatted_name)->toBe('Joao Souza');
});

it('filters users by search scope on name and email', function (): void {
    $matchedByName = User::factory()->create(['name' => 'Carlos Pereira', 'email' => 'carlos@example.com']);
    $matchedByMail = User::factory()->create(['name' => 'Ana Paula', 'email' => 'ana.match@example.com']);
    $notMatched    = User::factory()->create(['name' => 'Bruno Costa', 'email' => 'bruno@example.com']);

    $users = User::query()->search('match')->get();

    expect($users->pluck('id')->all())
        ->toContain($matchedByMail->id)
        ->not->toContain($matchedByName->id, $notMatched->id);

    $usersByName = User::query()->search('Carlos')->get();

    expect($usersByName->pluck('id')->all())
        ->toContain($matchedByName->id)
        ->not->toContain($matchedByMail->id, $notMatched->id);
});

it('returns true only when user type is admin', function (): void {
    $admin = User::factory()->create(['type' => TypeUsers::Admin]);
    $user  = User::factory()->create(['type' => TypeUsers::User]);

    expect($admin->isAdmin())->toBeTrue()
        ->and($user->isAdmin())->toBeFalse();
});

<?php

declare(strict_types = 1);

use App\Models\User;
use Illuminate\Testing\TestResponse;

use function Pest\Laravel\getJson;

function getUsers(array $params = []): TestResponse
{
    return getJson(route('search.users', $params));
}

it('should get get users', function (): void {
    getUsers()->assertOk();
});

it('should return a paginated list of users', function (): void {
    User::factory()->count(20)->create();

    getUsers()
        ->assertJsonCount(10, 'data')
        ->assertJsonPath('meta.current_page', 1)
        ->assertJsonPath('meta.per_page', 10)
        ->assertJsonPath('meta.total', 20);
});

it('should be able to get next page', function (): void {
    User::factory()->count(20)->create();

    getUsers(['page' => 2])
        ->assertJsonCount(10, 'data')
        ->assertJsonPath('meta.current_page', 2)
        ->assertJsonPath('meta.per_page', 10)
        ->assertJsonPath('meta.total', 20);
});

it('should return id and name of users', function (): void {
    /** @var User $user */
    $user = User::factory()->create();

    getUsers()
        ->assertJsonPath('data.0', [
            'id'   => $user->id,
            'name' => $user->name,
        ]);
});

it('should be able to search a particular user', function (): void {
    $name = 'João ' . random_int(1, 999);

    User::factory()->create(['name' => $name]);

    User::factory()->count(20)->create();

    getUsers(['search' => $name])
        ->assertJsonCount(1, 'data')
        ->assertJsonPath('meta.current_page', 1)
        ->assertJsonPath('meta.per_page', 10)
        ->assertJsonPath('meta.total', 1);
});

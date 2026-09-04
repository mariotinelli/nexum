<?php

declare(strict_types = 1);

/*
|--------------------------------------------------------------------------
| Test Case
|--------------------------------------------------------------------------
|
| The closure you provide to your test functions is always bound to a specific PHPUnit test
| case class. By default, that class is "PHPUnit\Framework\TestCase". Of course, you may
| need to change it using the "pest()" function to bind a different classes or traits.
|
*/

use App\Enums\Toast;
use App\Models\User;
use Illuminate\Contracts\Auth\Authenticatable;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Livewire\Component;
use Livewire\Features\SupportTesting\Testable;

use function Pest\Laravel\actingAs;

use Tests\TestCase;

pest()->extend(TestCase::class)
    ->use(RefreshDatabase::class)
    ->in('Feature', 'Unit', 'Brain');

pest()->extend(TestCase::class)
    ->in('Browser');

/*
|--------------------------------------------------------------------------
| Expectations
|--------------------------------------------------------------------------
|
| When you're writing tests, you often need to check that values meet certain conditions. The
| "expect()" function gives you access to a set of "expectations" methods that you can use
| to assert different things. Of course, you may extend the Expectation API at any time.
|
*/

/*
|--------------------------------------------------------------------------
| Functions
|--------------------------------------------------------------------------
|
| While Pest is very powerful out-of-the-box, you may have some testing code specific to your
| project that you don't want to repeat in every file. Here you can also expose helpers as
| global functions to help you to reduce the number of lines of code in your test files.
|
*/

function actingAsAdmin(): User
{
    /** @var User|Authenticatable $user */
    $user = User::factory()
        ->admin()
        ->create();

    actingAs($user);

    return $user;
}

function actingAsUser(BackedEnum | array | null $permission = null): User
{
    /** @var User|Authenticatable $user */
    $user = User::factory()
        ->user()
        ->create();

    if ($permission) {
        $user->givePermissionTo($permission);
    }

    actingAs($user);

    return $user;
}

Testable::macro('assertToast', function (string $title, ?string $description = null, Toast $type = Toast::Success, int $time = 7, bool $nextPage = false, bool $persistent = false): Testable {
    if ($nextPage) {
        $this->assertSessionHas('toast', [
            [
                'title'       => $title,
                'description' => $description,
                'type'        => $type->value,
                'time'        => $time,
                'persistent'  => $persistent,
            ],
        ]);

        return $this;
    }

    /** @var Testable|Component $this */
    $this->assertDispatched('toast', title: $title, description: $description, type: $type->value, time: $time, persistent: $persistent);

    return $this;
});

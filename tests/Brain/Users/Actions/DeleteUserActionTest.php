<?php

declare(strict_types = 1);

use App\Brain\Users\Actions\DeleteUserAction;
use App\Models\User;

use function Pest\Laravel\assertSoftDeleted;

it('soft deletes a user', function (): void {
    $user = User::factory()->user()->create();

    DeleteUserAction::dispatchSync([
        'user' => $user,
    ]);

    assertSoftDeleted($user);
});

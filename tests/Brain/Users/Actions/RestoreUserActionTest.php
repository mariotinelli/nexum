<?php

declare(strict_types = 1);

use App\Brain\Users\Actions\RestoreUserAction;
use App\Models\User;

use function Pest\Laravel\assertNotSoftDeleted;

it('restores a soft deleted user', function (): void {
    $user = User::factory()->user()->create();
    $user->delete();

    RestoreUserAction::dispatchSync([
        'user' => $user,
    ]);

    assertNotSoftDeleted($user);
});

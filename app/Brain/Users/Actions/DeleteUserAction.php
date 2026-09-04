<?php

declare(strict_types = 1);

namespace App\Brain\Users\Actions;

use App\Models\User;
use Brain\Action;

/**
 * Action DeleteUserAction
 *
 * @property-read User $user
 */
class DeleteUserAction extends Action
{
    public function handle(): self
    {
        $this->user->delete();

        return $this;
    }
}

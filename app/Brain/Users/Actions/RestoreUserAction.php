<?php

declare(strict_types = 1);

namespace App\Brain\Users\Actions;

use App\Models\User;
use Brain\Action;

/**
 * Action RestoreUserAction
 *
 * @property-read User $user
 */
class RestoreUserAction extends Action
{
    public function handle(): self
    {
        $this->user->restore();

        return $this;
    }
}

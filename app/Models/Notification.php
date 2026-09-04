<?php

declare(strict_types = 1);

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Notifications\DatabaseNotification;

class Notification extends DatabaseNotification
{
    use HasFactory;

    protected function casts(): array
    {
        return [
            ...parent::casts(),
            'viewed_at' => 'datetime',
        ];
    }
}

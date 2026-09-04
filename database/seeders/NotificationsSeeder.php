<?php

declare(strict_types = 1);

namespace Database\Seeders;

use App\Models\Notification;
use App\Models\User;
use Illuminate\Database\Seeder;

class NotificationsSeeder extends Seeder
{
    public function run(): void
    {

        $data = [
            [
                'user_id' => User::first()->id,
                'data'    => [
                    'title'    => 'Brand Export Completed',
                    'body'     => 'Your brand export has completed and 400 rows exported.',
                    'icon'     => 'document-plus',
                    'redirect' => '#',
                ],
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'user_id' => User::first()->id,
                'data'    => [
                    'title'    => 'New User Registered',
                    'body'     => 'A new user has been registered.',
                    'icon'     => 'user-group',
                    'redirect' => null,
                ],
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'user_id' => User::first()->id,
                'data'    => [
                    'title'    => 'New User Registered',
                    'body'     => 'A new user has been registered.',
                    'icon'     => 'user-group',
                    'redirect' => null,
                ],
                'created_at' => now(),
                'updated_at' => now(),
            ]];

        Notification::insert($data);
    }
}

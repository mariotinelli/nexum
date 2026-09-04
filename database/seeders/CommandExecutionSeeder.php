<?php

declare(strict_types = 1);

namespace Database\Seeders;

use App\Models\CommandExecution;
use Illuminate\Database\Seeder;

class CommandExecutionSeeder extends Seeder
{
    public function run(): void
    {
        CommandExecution::factory()
            ->count(120)
            ->create();
    }
}

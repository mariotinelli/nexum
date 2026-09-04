<?php

declare(strict_types = 1);

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class RegionSeeder extends Seeder
{
    public function run(): void
    {
        DB::table('regions')->insert([
            [
                'name' => 'Norte',
            ],
            [
                'name' => 'Nordeste',
            ],
            [
                'name' => 'Sudeste',
            ],
            [
                'name' => 'Centro-Oeste',
            ],
            [
                'name' => 'Sul',
            ],
        ]);
    }
}

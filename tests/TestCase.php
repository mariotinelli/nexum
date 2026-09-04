<?php

declare(strict_types = 1);

namespace Tests;

use Database\Seeders\PermissionSeeder;
use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    protected function setUp(): void
    {
        parent::setUp();

        $this->seed(PermissionSeeder::class);
    }
}

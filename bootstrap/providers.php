<?php

declare(strict_types = 1);
use App\Dev\Providers\DevServiceProvider;
use App\Providers\AppServiceProvider;
use App\Providers\QueueServiceProvider;
use OwenIt\Auditing\AuditingServiceProvider;

return [
    DevServiceProvider::class,
    AppServiceProvider::class,
    QueueServiceProvider::class,
    AuditingServiceProvider::class,
];

<?php

declare(strict_types = 1);

use App\View\Components\AppLayout;
use App\View\Components\GuestLayout;

it('renders app layout component view', function (): void {
    $view = (new AppLayout())->render();

    expect($view->name())->toBe('layouts.app');
});

it('renders guest layout component view', function (): void {
    $view = (new GuestLayout())->render();

    expect($view->name())->toBe('layouts.guest');
});

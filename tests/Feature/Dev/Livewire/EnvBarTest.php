<?php

declare(strict_types = 1);

use App\Dev\Livewire\EnvBar;

use function Pest\Livewire\livewire;

it('should return the current app env', function (): void {
    config()->set('app.env', 'production');

    livewire(EnvBar::class)
        ->assertSet('env', 'production');
});

it('should return null branch when app is not local', function (): void {
    config()->set('app.env', 'production');

    livewire(EnvBar::class)
        ->assertSet('branch', null);
});

it('should render the env bar template', function (): void {
    $template = (new EnvBar())->render();

    expect($template)->toContain('<x-ui.badge md :label="$this->env" />')
        ->and($template)->toContain('@if(app()->isLocal())');
});

it('should return branch value when app is local', function (): void {
    app()->detectEnvironment(fn (): string => 'local');

    $branch = (new EnvBar())->branch();

    expect(is_string($branch))->toBeTrue();

    app()->detectEnvironment(fn (): string => 'testing');
});

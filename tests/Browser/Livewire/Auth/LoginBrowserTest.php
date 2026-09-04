<?php

declare(strict_types = 1);

use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

it('renders the split admin login on desktop without JavaScript errors', function (): void {
    visit('/admin/login')
        ->assertSee('Área administrativa')
        ->assertPresent('input[name=email]')
        ->assertPresent('input[name=password]')
        ->assertSee('Lembrar-me')
        ->assertNoJavaScriptErrors()
        ->screenshot(fullPage: false, filename: 'admin-login-desktop');
});

it('renders the responsive admin login on mobile without JavaScript errors', function (): void {
    visit('/admin/login')
        ->on()->mobile()
        ->assertSee('Área administrativa')
        ->assertPresent('input[name=email]')
        ->assertPresent('input[name=password]')
        ->assertNoJavaScriptErrors()
        ->screenshot(fullPage: true, filename: 'admin-login-mobile');
});

it('renders the centered guest layout on password recovery', function (): void {
    visit('/admin/esqueci-minha-senha')
        ->assertSee('Esqueci minha senha')
        ->assertPresent('input[name=email]')
        ->assertNoJavaScriptErrors()
        ->screenshot(fullPage: false, filename: 'admin-forgot-password-centered');
});

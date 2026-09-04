<?php

declare(strict_types = 1);

use App\Models\CommandExecution;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

it('shows history and console output in modal', function (): void {
    actingAsAdmin();

    $execution = CommandExecution::factory()->create([
        'command' => 'php artisan about',
        'output'  => "Linha 1\nLinha 2",
    ]);

    $page = visit(route('admin.support.artisan-commands.index'));

    $page
        ->assertSee('Executor de Comandos Artisan')
        ->assertSee('php artisan about')
        ->click("#show-output-button-{$execution->id}")
        ->assertSee('Saída do comando')
        ->assertSee('Linha 1')
        ->assertNoJavaScriptErrors();
});

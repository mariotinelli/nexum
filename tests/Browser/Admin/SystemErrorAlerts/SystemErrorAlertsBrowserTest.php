<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Models\SystemErrorAlert;
use App\Models\User;

use function Pest\Laravel\actingAs;

it('allows viewing error alerts list and details', function (): void {
    /** @var User $supportUser */
    $supportUser = User::factory()->create([
        'type' => TypeUsers::SupportRemSoft,
    ]);

    actingAs($supportUser);

    $alert = SystemErrorAlert::factory()->create([
        'exception_class' => 'RuntimeException',
        'message'         => 'Erro crítico durante o processamento.',
    ]);

    $page = visit(route('admin.support.system-error-alerts.index'));

    $page
        ->assertSee('Alertas de Erro')
        ->waitForText('RuntimeException')
        ->assertSee('RuntimeException')
        ->click("#show-system-error-alert-{$alert->id}")
        ->assertSee('Detalhes do Alerta')
        ->assertSee('Erro crítico durante o processamento.')
        ->assertNoJavaScriptErrors();
});

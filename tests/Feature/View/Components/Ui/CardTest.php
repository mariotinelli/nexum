<?php

declare(strict_types = 1);

it('renders collapsible card open by default', function (): void {
    $view = $this->blade('<x-ui.card header="Card" collapse>Conteudo</x-ui.card>');

    $view->assertSee('x-data="{ open: true }"', false)
        ->assertSee('x-collapse.duration.300ms', false)
        ->assertSee('@click="open = ! open"', false);
});

it('renders collapsible card closed when collapsed is true', function (): void {
    $view = $this->blade('<x-ui.card header="Card" collapse collapsed>Conteudo</x-ui.card>');

    $view->assertSee('x-data="{ open: false }"', false)
        ->assertSee('x-collapse.duration.300ms', false);
});

it('does not render collapse attributes when collapse is disabled', function (): void {
    $view = $this->blade('<x-ui.card header="Card">Conteudo</x-ui.card>');

    $view->assertDontSee('x-collapse.duration.400ms', false)
        ->assertDontSee('x-data="{ open:', false)
        ->assertDontSee('@click="open = ! open"', false);
});

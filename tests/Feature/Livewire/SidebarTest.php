<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;
use App\Livewire\Sidebar;
use App\Models\User;
use App\Support\Navigation\SidebarGroup;

use function Pest\Livewire\livewire;

it('renders the sidebar with the visible groups for an administrator', function (): void {
    actingAsAdmin();

    livewire(Sidebar::class)
        ->assertOk()
        ->assertSee('Dashboard')
        ->assertSee('Gestão')
        ->assertSee('Usuários')
        ->assertSee('Perfis')
        ->assertSet('groups', function (array $groups): bool {
            $routes = collect($groups)
                ->flatMap(fn (SidebarGroup $group): array => collect($group->items)->pluck('route')->all());

            expect($routes)->toContain('admin.dashboard')
                ->toContain('admin.management.users.index')
                ->toContain('admin.management.roles.index');

            return true;
        });
});

it('renders only the support menu for a support user', function (): void {
    $support = User::factory()->create([
        'role_id' => null,
        'type'    => TypeUsers::SupportRemSoft,
    ]);

    $this->actingAs($support);

    livewire(Sidebar::class)
        ->assertOk()
        ->assertSee('Suporte')
        ->assertSee('Alertas de Erro')
        ->assertDontSee('Dashboard')
        ->assertDontSee('Comandos')
        ->assertSet('groups', function (array $groups): bool {
            $routes = collect($groups)
                ->flatMap(fn (SidebarGroup $group): array => collect($group->items)->pluck('route')->all())
                ->values()
                ->all();

            expect($routes)->toBe(['admin.support.system-error-alerts.index']);

            return true;
        });
});

it('does not expose menu groups to guests', function (): void {
    livewire(Sidebar::class)
        ->assertOk()
        ->assertSet('groups', []);
});

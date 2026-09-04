<?php

declare(strict_types = 1);

use App\Enums\Permissions\Management\RolePermissions;
use App\Models\Role;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Browser\Support\CrudBrowserTemplate;

uses(RefreshDatabase::class);

it('covers roles crud flow with modal submit and persistence', function (): void {
    actingAsAdmin();

    $existingRole = Role::factory()->create([
        'name'        => 'Perfil Browser Base',
        'description' => 'Descrição inicial do perfil',
    ]);

    $existingRole->syncPermissions([RolePermissions::View->value]);

    $page = visit(route('admin.management.roles.index'));

    CrudBrowserTemplate::run($page, [
        'indexTitle' => 'Perfis',
        'create'     => [
            'open'        => '#create-role-button',
            'modalTitle'  => 'Novo Perfil',
            'nameField'   => '#create-role-name',
            'name'        => 'Perfil Browser Novo',
            'extraFields' => [
                '#create-role-description' => 'Descrição Browser Novo',
            ],
            'clicks' => [
                '#create-role-modal #select-all-permissions',
            ],
            'submit' => '#create-role-modal #save-button',
            'toast'  => 'Perfil cadastrado com sucesso',
        ],
        'update' => [
            'open'       => "#edit-role-button-{$existingRole->id}",
            'modalTitle' => 'Editar Perfil',
            'nameField'  => '#update-role-name',
            'oldName'    => 'Perfil Browser Base',
            'newName'    => 'Perfil Browser Atualizado',
            'submit'     => '#update-role-modal #save-button',
            'toast'      => 'Perfil atualizado com sucesso',
        ],
    ]);

    $createdRole = Role::query()->where('name', 'Perfil Browser Novo')->first();

    expect($createdRole)->not->toBeNull()
        ->and($createdRole?->description)->toBe('Descrição Browser Novo');

    $existingRole->refresh();

    expect($existingRole->name)->toBe('Perfil Browser Atualizado');
});

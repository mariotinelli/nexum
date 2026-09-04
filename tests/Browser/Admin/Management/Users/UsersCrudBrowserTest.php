<?php

declare(strict_types = 1);

use App\Models\Role;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Browser\Support\CrudBrowserTemplate;

uses(RefreshDatabase::class);

it('covers users crud flow with modal submit and persistence', function (): void {
    actingAsAdmin();

    $role = Role::factory()->create([
        'name' => 'Perfil Browser Users',
    ]);

    $existingUser = User::factory()->user()->create([
        'name'    => 'Usuário Browser Base',
        'email'   => 'browser.base@example.com',
        'role_id' => $role->id,
    ]);

    $page = visit(route('admin.management.users.index'));

    CrudBrowserTemplate::run($page, [
        'indexTitle' => 'Usuários',
        'create'     => [
            'open'        => '#create-user-button',
            'modalTitle'  => 'Novo Usuário',
            'nameField'   => '#create-user-name',
            'name'        => 'Usuário Browser Novo',
            'extraFields' => [
                '#create-user-email' => 'browser.new@example.com',
            ],
            'usageSelect'    => '#create-user-role',
            'usageOption'    => 'Perfil Browser Users',
            'relationSelect' => '#create-user-role',
            'relationOption' => 'Perfil Browser Users',
            'submit'         => '#create-user-modal #save-button',
            'toast'          => 'Usuário cadastrado com sucesso',
        ],
        'update' => [
            'open'       => "#edit-user-button-{$existingUser->id}",
            'modalTitle' => 'Editar Usuário',
            'nameField'  => '#update-user-name',
            'oldName'    => 'Usuário Browser Base',
            'newName'    => 'Usuário Browser Atualizado',
            'submit'     => '#update-user-modal #save-button',
            'toast'      => 'Usuário atualizado com sucesso',
        ],
        'delete' => [
            'open'   => "#delete-user-button-{$existingUser->id}",
            'submit' => '#delete-button',
            'status' => 'Inativo',
            'toast'  => 'Usuário desativado com sucesso',
        ],
        'restore' => [
            'open'   => "#restore-user-button-{$existingUser->id}",
            'submit' => '#restore-button',
            'status' => 'Ativo',
            'toast'  => 'Usuário ativado com sucesso',
        ],
    ]);

    $createdUser = User::query()->where('email', 'browser.new@example.com')->first();

    expect($createdUser)->not->toBeNull()
        ->and($createdUser?->role_id)->toBe($role->id);

    $existingUser->refresh();

    expect($existingUser->name)->toBe('Usuário Browser Atualizado')
        ->and($existingUser->trashed())->toBeFalse();
});

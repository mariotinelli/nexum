<?php

declare(strict_types = 1);

use App\Enums\TypeUsers;

it('returns expected labels for each user type', function (): void {
    expect(TypeUsers::Admin->label())->toBe('Administrador')
        ->and(TypeUsers::User->label())->toBe('Usuário')
        ->and(TypeUsers::Customer->label())->toBe('Cliente')
        ->and(TypeUsers::SupportRemSoft->label())->toBe('Suporte Rem Soft');
});

it('returns user types as array', function (): void {
    expect(TypeUsers::toArray())->toBe([
        1 => 'Administrador',
        2 => 'Usuário',
        3 => 'Cliente',
        4 => 'Suporte Rem Soft',
    ]);
});

it('identifies the user types allowed in the admin area', function (): void {
    expect(TypeUsers::Admin->canAccessAdminArea())->toBeTrue()
        ->and(TypeUsers::User->canAccessAdminArea())->toBeTrue()
        ->and(TypeUsers::SupportRemSoft->canAccessAdminArea())->toBeTrue()
        ->and(TypeUsers::Customer->canAccessAdminArea())->toBeFalse()
        ->and(TypeUsers::adminAreaValues())->toBe([
            TypeUsers::Admin->value,
            TypeUsers::User->value,
            TypeUsers::SupportRemSoft->value,
        ]);
});

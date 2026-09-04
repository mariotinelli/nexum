<?php

declare(strict_types = 1);

use App\Enums\AcceptedTypes;

it('returns expected labels for each accepted type', function (): void {
    expect(AcceptedTypes::Image->label())->toBe('Imagem')
        ->and(AcceptedTypes::Doc->label())->toBe('DOC')
        ->and(AcceptedTypes::Pdf->label())->toBe('PDF')
        ->and(AcceptedTypes::Video->label())->toBe('Vídeo');
});

it('returns expected mime types for each accepted type', function (): void {
    expect(AcceptedTypes::Image->mimes())->toBe(['image/*'])
        ->and(AcceptedTypes::Doc->mimes())->toBe([
            'application/msword',
            'application/vnd.ms-word',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        ])
        ->and(AcceptedTypes::Pdf->mimes())->toBe(['application/pdf'])
        ->and(AcceptedTypes::Video->mimes())->toBe(['video/*']);
});

it('returns default accepted mime types', function (): void {
    expect(AcceptedTypes::default())->toBe('image/*,application/pdf');
});

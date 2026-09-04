<?php

declare(strict_types = 1);

use App\Actions\Media\CreateMedia;
use App\Models\Address;
use App\Models\Media;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

use function Pest\Laravel\assertDatabaseHas;

beforeEach(function (): void {
    $this->disk = 'media-test';
});

it('creates media and stores uploaded file in configured disk', function (): void {
    config()->set('filesystems.default', $this->disk);
    Storage::fake($this->disk);

    $model = Address::factory()->create();
    $file  = UploadedFile::fake()->image('profile.png', 200, 200);

    $media = (new CreateMedia())->handle($model, 'documents', $file);

    expect($media)
        ->toBeInstanceOf(Media::class)
        ->and($media->entity_id)->toBe($model->id)
        ->and($media->entity_type)->toBe($model->getMorphClass())
        ->and($media->collection)->toBe('documents')
        ->and($media->original_name)->toBe('profile.png')
        ->and($media->type)->toBe('png')
        ->and($media->disk)->toBe($this->disk)
        ->and($media->size)->toBe($file->getSize())
        ->and(pathinfo($media->name, PATHINFO_EXTENSION))->toBe('png');

    expect(Storage::disk($this->disk)->exists("documents/{$media->name}"))->toBeTrue();

    assertDatabaseHas('media', [
        'id'            => $media->id,
        'entity_id'     => $model->id,
        'entity_type'   => $model->getMorphClass(),
        'name'          => $media->name,
        'collection'    => 'documents',
        'original_name' => 'profile.png',
        'type'          => 'png',
        'disk'          => $this->disk,
        'size'          => (string) $file->getSize(),
    ]);
});

it('creates media preserving original name and extension for non image files', function (): void {
    config()->set('filesystems.default', 'media-private');
    Storage::fake('media-private');

    $model = Address::factory()->create();
    $file  = UploadedFile::fake()->create('contract.pdf', 512, 'application/pdf');

    $media = (new CreateMedia())->handle($model, 'contracts', $file);

    expect($media->original_name)->toBe('contract.pdf')
        ->and($media->type)->toBe('pdf')
        ->and($media->disk)->toBe('media-private')
        ->and(pathinfo($media->name, PATHINFO_EXTENSION))->toBe('pdf')
        ->and($media->name)->not->toBe('contract.pdf');

    expect(Storage::disk('media-private')->exists("contracts/{$media->name}"))->toBeTrue();

    assertDatabaseHas('media', [
        'id'          => $media->id,
        'collection'  => 'contracts',
        'type'        => 'pdf',
        'disk'        => 'media-private',
        'entity_id'   => $model->id,
        'entity_type' => $model->getMorphClass(),
    ]);
});

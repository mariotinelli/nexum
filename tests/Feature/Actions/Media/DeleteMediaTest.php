<?php

declare(strict_types = 1);

use App\Actions\Media\DeleteMedia;
use App\Models\Address;
use App\Models\Media;
use Illuminate\Support\Facades\Storage;

use function Pest\Laravel\assertDatabaseHas;
use function Pest\Laravel\assertDatabaseMissing;

beforeEach(function (): void {
    $this->disk = 'media-test';
});

it('deletes selected media from storage and database', function (): void {
    Storage::fake($this->disk);

    $model = Address::factory()->create();

    $firstMedia = Media::factory()->entity($model)->create([
        'name'       => 'file-one.png',
        'collection' => 'documents',
        'type'       => 'png',
        'disk'       => $this->disk,
    ]);

    $secondMedia = Media::factory()->entity($model)->create([
        'name'       => 'file-two.png',
        'collection' => 'documents',
        'type'       => 'png',
        'disk'       => $this->disk,
    ]);

    Storage::disk($this->disk)->put($firstMedia->getPath(), 'content 1');
    Storage::disk($this->disk)->put($secondMedia->getPath(), 'content 2');

    expect(Storage::disk($this->disk)->exists($firstMedia->getPath()))->toBeTrue()
        ->and(Storage::disk($this->disk)->exists($secondMedia->getPath()))->toBeTrue();

    (new DeleteMedia())->handle($model, [$firstMedia->id, $secondMedia->id]);

    expect(Storage::disk($this->disk)->exists($firstMedia->getPath()))->toBeFalse()
        ->and(Storage::disk($this->disk)->exists($secondMedia->getPath()))->toBeFalse();

    assertDatabaseMissing('media', ['id' => $firstMedia->id]);
    assertDatabaseMissing('media', ['id' => $secondMedia->id]);
});

it('deletes only media that belongs to the given model', function (): void {
    Storage::fake($this->disk);

    $targetModel = Address::factory()->create();
    $otherModel  = Address::factory()->create();

    $targetMedia = Media::factory()->entity($targetModel)->create([
        'name'       => 'target-file.png',
        'collection' => 'documents',
        'type'       => 'png',
        'disk'       => $this->disk,
    ]);

    $otherMedia = Media::factory()->entity($otherModel)->create([
        'name'       => 'other-file.png',
        'collection' => 'documents',
        'type'       => 'png',
        'disk'       => $this->disk,
    ]);

    Storage::disk($this->disk)->put($targetMedia->getPath(), 'target content');
    Storage::disk($this->disk)->put($otherMedia->getPath(), 'other content');

    (new DeleteMedia())->handle($targetModel, [$targetMedia->id, $otherMedia->id]);

    expect(Storage::disk($this->disk)->exists($targetMedia->getPath()))->toBeFalse()
        ->and(Storage::disk($this->disk)->exists($otherMedia->getPath()))->toBeTrue();

    assertDatabaseMissing('media', ['id' => $targetMedia->id]);
    assertDatabaseHas('media', ['id' => $otherMedia->id, 'entity_id' => $otherModel->id]);
});

<?php

declare(strict_types = 1);

use App\Models\Address;
use App\Models\Media;
use Illuminate\Database\Eloquent\Relations\MorphTo;
use Illuminate\Support\Facades\Storage;

it('returns entity morph relation', function (): void {
    $media = Media::factory()->make();

    expect($media->entity())->toBeInstanceOf(MorphTo::class);
});

it('returns full media path from collection and name', function (): void {
    $media = Media::factory()->make([
        'collection' => 'documents',
        'name'       => 'file.png',
    ]);

    expect($media->getPath())->toBe('documents/file.png');
});

it('returns temporary url from configured disk and path', function (): void {
    $media = Media::factory()->make([
        'disk'       => 'media-test',
        'collection' => 'documents',
        'name'       => 'file.png',
    ]);

    Storage::shouldReceive('disk')->once()->with('media-test')->andReturnSelf();
    Storage::shouldReceive('temporaryUrl')
        ->once()
        ->with('documents/file.png', Mockery::type(DateTimeInterface::class))
        ->andReturn('https://example.test/documents/file.png');

    expect($media->getUrl())->toBe('https://example.test/documents/file.png');
});

it('resolves entity relation to the polymorphic model', function (): void {
    $address = Address::factory()->create();
    $media   = Media::factory()->entity($address)->create();

    expect($media->entity)->toBeInstanceOf(Address::class)
        ->and($media->entity->id)->toBe($address->id);
});

<?php

declare(strict_types = 1);

namespace App\Actions\Media;

use App\Models\Media;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Storage;

class DeleteMedia
{
    public function handle(Model $model, array $mediaIds): void
    {
        $media = Media::query()
            ->where('entity_id', $model->getKey())
            ->where('entity_type', $model->getMorphClass())
            ->whereIn('id', $mediaIds);

        foreach ($media->get() as $item) {
            Storage::disk($item->disk)->delete($item->getPath());
        }

        $media->delete();
    }
}

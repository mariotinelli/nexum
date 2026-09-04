<?php

declare(strict_types = 1);

namespace App\Actions\Media;

use App\Models\Media;

class GetMedia
{
    public function handle(Media $media): array
    {
        return [
            'id'        => $media->id,
            'name'      => $media->original_name,
            'preview'   => $media->getUrl(),
            'type'      => $media->type,
            'size'      => $media->size,
            'updatedAt' => $media->updated_at,
        ];
    }
}

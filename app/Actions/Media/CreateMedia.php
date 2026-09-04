<?php

declare(strict_types = 1);

namespace App\Actions\Media;

use App\Models\Media;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Http\UploadedFile;
use Livewire\Features\SupportFileUploads\TemporaryUploadedFile;

class CreateMedia
{
    public function handle(Model $model, string $collection, TemporaryUploadedFile | UploadedFile $file): Media
    {
        $fileName = uniqid() . '.' . $file->getClientOriginalExtension();

        $file->storeAs(path: $collection, name: $fileName, options: [
            'disk' => config('filesystems.default'),
        ]);

        return Media::query()->create([
            'entity_id'     => $model->getKey(),
            'entity_type'   => $model->getMorphClass(),
            'name'          => $fileName,
            'collection'    => $collection,
            'original_name' => $file->getClientOriginalName(),
            'type'          => $file->getClientOriginalExtension(),
            'disk'          => config('filesystems.default'),
            'size'          => $file->getSize(),
        ]);
    }
}

<?php

declare(strict_types = 1);

namespace App\Http\Resources\Search;

use Illuminate\Http\Resources\Json\JsonResource;

/**
 * @property-read int $id
 * @property-read string $name
 */
class UserResource extends JsonResource
{
    public function toArray($request): array
    {
        return [
            'id'   => $this->id,
            'name' => $this->name,
        ];
    }
}

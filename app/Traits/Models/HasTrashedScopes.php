<?php

declare(strict_types = 1);

namespace App\Traits\Models;

use App\Enums\Status;
use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

trait HasTrashedScopes
{
    #[Scope]
    protected function filterByTrashed(Builder $query, ?Status $status): Builder
    {
        $deletedAtColumn = method_exists($query->getModel(), 'getQualifiedDeletedAtColumn')
            ? $query->getModel()->getQualifiedDeletedAtColumn()
            : $query->getModel()->qualifyColumn('deleted_at');

        return match ($status) {
            Status::All         => $query->withoutGlobalScope(SoftDeletingScope::class),
            Status::Active      => $query->whereNull($deletedAtColumn),
            Status::Deactivated => $query
                ->withoutGlobalScope(SoftDeletingScope::class)
                ->whereNotNull($deletedAtColumn),
            default => $query,
        };
    }
}

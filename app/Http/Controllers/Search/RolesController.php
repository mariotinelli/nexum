<?php

declare(strict_types = 1);

namespace App\Http\Controllers\Search;

use App\Http\Resources\Search\RoleResource;
use App\Models\Role;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class RolesController extends BaseSearchController
{
    public function __invoke()
    {
        $roles = $this->getRoles();

        if (request()->has('selected') && !request()->has('page')) {
            $roles = $this->getSelected(Role::class, $roles);
        }

        return RoleResource::collection($roles);
    }

    protected function getRoles(): LengthAwarePaginator
    {
        return Role::query()
            ->when(
                request()->has('search'),
                fn (Builder $query) => $query->where('name', 'like', '%' . request()->get('search') . '%')
            )
            ->when(
                request()->has('selected'),
                fn (Builder $query) => $query->whereNotIn('id', request()->get('selected'))
            )
            ->orderBy('name')
            ->paginate(10);
    }
}

<?php

declare(strict_types = 1);

namespace App\Http\Controllers\Search;

use App\Http\Resources\Search\UserResource;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class UsersController extends BaseSearchController
{
    public function __invoke()
    {
        $users = $this->getUsers();

        if (request()->has('selected') && !request()->has('page')) {
            $users = $this->getSelected(User::class, $users);
        }

        return UserResource::collection($users);
    }

    protected function getUsers(): LengthAwarePaginator
    {
        return User::query()
            ->when(
                request()->has('search'),
                fn (Builder $query) => $query->whereLike('name', '%' . request('search') . '%')
            )
            ->when(
                request()->has('selected'),
                fn (Builder $query) => $query->whereNotIn('id', request()->get('selected'))
            )
            ->orderBy('name')
            ->paginate(10);
    }
}

<?php

declare(strict_types = 1);

namespace App\Http\Controllers\Search;

use App\Http\Resources\Search\StateResource;
use App\Models\State;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;
use Illuminate\Pagination\LengthAwarePaginator;

class StatesController extends BaseSearchController
{
    public function __invoke(): AnonymousResourceCollection
    {
        $states = $this->getStates();

        if (request()->has('selected') && !request()->has('page')) {
            $states = $this->getSelected(State::class, $states);
        }

        return StateResource::collection($states);
    }

    protected function getStates(): LengthAwarePaginator
    {
        return State::query()
            ->when(
                request()->has('search'),
                fn (Builder $query): Builder => $query->whereLike('name', '%' . request()->string('search')->toString() . '%')
            )
            ->when(
                request()->has('selected'),
                fn (Builder $query): Builder => $query->whereNotIn('id', (array) request()->get('selected'))
            )
            ->orderBy('name')
            ->paginate(10);
    }
}

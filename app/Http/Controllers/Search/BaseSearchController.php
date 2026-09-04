<?php

declare(strict_types = 1);

namespace App\Http\Controllers\Search;

use App\Http\Controllers\Controller;
use Illuminate\Pagination\LengthAwarePaginator;

abstract class BaseSearchController extends Controller
{
    protected function getSelected(string $model, LengthAwarePaginator $options): LengthAwarePaginator
    {
        $selected = app($model)::query()
            ->whereIn(request()->get('selectedColumn', 'id'), request()->get('selected'))
            ->get();

        return $options->setCollection($selected->merge($options));
    }
}

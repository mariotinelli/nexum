<?php

declare(strict_types = 1);

use App\Enums\SortDirection;
use App\Traits\Components\WithTable;

it('sorts by new key and toggles direction when key repeats', function (): void {
    $component = new class () {
        use WithTable;

        public function resetPage($pageName = 'page'): void
        {
        }
    };

    $component->sortBy('name');
    expect($component->sortKeyName)->toBe('name')
        ->and($component->sortDirection)->toBe(SortDirection::Asc->value);

    $component->sortBy('name');
    expect($component->sortDirection)->toBe(SortDirection::Desc->value);

    $component->sortBy('name');
    expect($component->sortDirection)->toBe(SortDirection::Asc->value);
});

it('resets pagination when search or filters are updated', function (): void {
    $component = new class () {
        use WithTable;

        public int $resetCounter = 0;

        public function resetPage($pageName = 'page'): void
        {
            $this->resetCounter++;
        }
    };

    $component->updatedSearch();
    $component->updatedFilters();

    expect($component->resetCounter)->toBe(2);
});

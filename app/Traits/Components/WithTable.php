<?php

declare(strict_types = 1);

namespace App\Traits\Components;

use App\Enums\SortDirection;
use Livewire\WithPagination;

trait WithTable
{
    use WithPagination;

    public int $perPage = 10;

    public array $perPageValues = [10, 25, 50];

    public string $search = '';

    public array $filters = [];

    public string $sortKeyName = 'id';

    public string $sortDirection = SortDirection::Desc->value;

    public bool $toggleOnlyTrashed = false;

    public function sortBy(string $key): void
    {
        if ($key === $this->sortKeyName) {
            $this->sortDirection = $this->sortDirection === SortDirection::Asc->value ? SortDirection::Desc->value : SortDirection::Asc->value;

            return;
        }

        $this->sortKeyName   = $key;
        $this->sortDirection = SortDirection::Asc->value;
    }

    public function updatedSearch(): void
    {
        $this->resetPage();
    }

    public function updatedFilters(): void
    {
        $this->resetPage();
    }
}

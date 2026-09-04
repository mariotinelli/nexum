<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Management\Users;

use App\Enums\Status;
use App\Enums\TypeUsers;
use App\Models\User;
use App\Traits\Components\WithTable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\View\View;
use Livewire\Attributes\Computed;
use Livewire\Attributes\On;
use Livewire\Component;

class Index extends Component
{
    use WithTable;

    #[On('users::refresh')]
    public function render(): View
    {
        return view('livewire.admin.management.users.index');
    }

    public function mount(): void
    {
        $this->authorize('view-any', User::class);

        $this->filters = $this->emptyFilters();

    }

    public function resetFilters(): void
    {
        $this->filters = $this->emptyFilters();
    }

    public function emptyFilters(): array
    {
        return [
            'roles'  => [],
            'status' => Status::All->value,
        ];
    }

    #[Computed]
    public function users(): LengthAwarePaginator
    {
        return User::query()
            ->with('role')
            ->where('type', TypeUsers::User)
            ->withTrashed()
            ->when($this->filters['roles'], fn (Builder $query): Builder => $query->whereIn('role_id', $this->filters['roles']))
            ->filterByTrashed(Status::tryFrom((string) $this->filters['status']))
            ->search($this->search)
            ->orderBy($this->sortKeyName, $this->sortDirection)
            ->paginate($this->perPage);
    }

    #[Computed]
    public function breadcrumb(): array
    {
        return [
            [
                'label' => 'Usuários',
            ],
        ];
    }
}

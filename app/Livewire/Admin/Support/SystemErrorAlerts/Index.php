<?php

declare(strict_types = 1);

namespace App\Livewire\Admin\Support\SystemErrorAlerts;

use App\Enums\SystemErrorAlertSeverities;
use App\Enums\SystemErrorAlertStatuses;
use App\Models\SystemErrorAlert;
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

    public function mount(): void
    {
        $this->authorize('view-any', SystemErrorAlert::class);

        $this->sortKeyName = 'last_seen_at';
        $this->filters     = $this->emptyFilters();
    }

    #[On('system-error-alerts::refresh')]
    public function render(): View
    {
        return view('livewire.admin.support.system-error-alerts.index');
    }

    public function emptyFilters(): array
    {
        return [
            'status'      => '',
            'severity'    => '',
            'environment' => '',
        ];
    }

    public function resetFilters(): void
    {
        $this->filters = $this->emptyFilters();
    }

    #[Computed]
    public function alerts(): LengthAwarePaginator
    {
        return SystemErrorAlert::query()
            ->with('user')
            ->select([
                'id',
                'status',
                'severity',
                'environment',
                'exception_class',
                'message',
                'request_method',
                'request_url',
                'user_id',
                'occurrences',
                'last_seen_at',
                'created_at',
            ])
            ->when($this->filters['status'] !== '', fn (Builder $query) => $query->where('status', (int) $this->filters['status']))
            ->when($this->filters['severity'] !== '', fn (Builder $query) => $query->where('severity', (int) $this->filters['severity']))
            ->when($this->filters['environment'] !== '', fn (Builder $query) => $query->where('environment', $this->filters['environment']))
            ->when($this->search, function (Builder $query): void {
                $query->where(function (Builder $subQuery): void {
                    $subQuery->where('exception_class', 'like', "%{$this->search}%")
                        ->orWhere('message', 'like', "%{$this->search}%")
                        ->orWhere('request_url', 'like', "%{$this->search}%");
                });
            })
            ->orderBy($this->sortKeyName, $this->sortDirection)
            ->paginate($this->perPage);
    }

    #[Computed]
    public function breadcrumb(): array
    {
        return [
            ['label' => 'Suporte'],
            ['label' => 'Alertas de Erro'],
        ];
    }

    #[Computed]
    public function environmentOptions(): array
    {
        return SystemErrorAlert::query()
            ->select('environment')
            ->distinct()
            ->orderBy('environment')
            ->pluck('environment', 'environment')
            ->toArray();
    }

    #[Computed]
    public function statuses(): array
    {
        return SystemErrorAlertStatuses::options();
    }

    #[Computed]
    public function severities(): array
    {
        return SystemErrorAlertSeverities::options();
    }
}

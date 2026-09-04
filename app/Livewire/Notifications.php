<?php

declare(strict_types = 1);

namespace App\Livewire;

use App\Traits\Components\WithSidepage;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Notifications\DatabaseNotification;
use Illuminate\Support\Collection as SupportCollection;
use Illuminate\View\View;
use Livewire\Attributes\Computed;
use Livewire\Attributes\On;
use Livewire\Component;

/**
 * @property-read Collection<int, DatabaseNotification> $notifications
 */
class Notifications extends Component
{
    use WithSidepage;

    #[On('notifications::updated')]
    public function render(): View
    {
        return view('livewire.notifications');
    }

    #[Computed]
    public function notifications(): Collection
    {
        return user()->notifications()->latest()->get();
    }

    #[Computed]
    public function unreadNotifications(): SupportCollection
    {
        return user()->unreadNotifications()->get();
    }

    public function markAllAsRead(): void
    {
        user()->unreadNotifications()->update(['read_at' => now()]);

        $this->dispatch('notifications::updated');
    }

    public function deleteAll(): void
    {
        user()->notifications()->delete();

        $this->dispatch('notifications::updated');
    }

    public function delete(string $notificationId): void
    {
        user()->notifications()->find($notificationId)?->delete();

        $this->dispatch('notifications::updated');
    }
}

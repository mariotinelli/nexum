<?php

declare(strict_types = 1);

namespace App\Livewire;

use App\Support\Navigation\SidebarMenuBuilder;
use Illuminate\Contracts\View\View;
use Livewire\Attributes\Computed;
use Livewire\Component;

class Sidebar extends Component
{
    public function render(): View
    {
        return view('livewire.sidebar');
    }

    #[Computed]
    public function groups(): array
    {
        return app(SidebarMenuBuilder::class)->buildFor(user());
    }
}

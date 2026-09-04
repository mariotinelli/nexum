<?php

declare(strict_types = 1);

namespace App\Dev\Livewire;

use Livewire\Attributes\Computed;
use Livewire\Component;

class EnvBar extends Component
{
    public function render(): string
    {
        return <<<'blade'
            <div class="flex items-center gap-x-2 ">
                <x-ui.badge md :label="$this->env" />

                @if(app()->isLocal())
                    <x-ui.badge md icon="branch" >
                        {{ $this->branch }}
                    </x-ui.badge>
                @endif
            </div>
        blade;
    }

    #[Computed]
    public function env(): string
    {
        return config('app.env');
    }

    #[Computed]
    public function branch(): ?string
    {
        if (app()->isLocal()) {
            return trim(shell_exec('git branch --show-current') ?: '');
        }

        return null;
    }
}

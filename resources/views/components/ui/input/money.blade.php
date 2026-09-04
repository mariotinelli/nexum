@props([
    'locale' => 'pt-BR',
    'prefix' => false,
])

@php
    $isLive    = $attributes->whereStartsWith('wire:model.live')->isNotEmpty();
    $isBlur    = $attributes->whereStartsWith('wire:model.blur')->isNotEmpty();
    $wireModel = $attributes->whereStartsWith('wire:model')->first();

    $debounce = 0;

    if ($isLive) {
        foreach ($attributes->getAttributes() as $key => $value) {
            if (str_starts_with($key, 'wire:model.live') && preg_match('/\.(\d+)ms$/', $key, $matches)) {
                $debounce = (int) $matches[1];

                break;
            }
        }
    }
@endphp

<div
    x-data="{
        wireModel: '{{ $wireModel }}',
        rawValue: @entangle($wireModel),
        displayValue: '',
        isLive: {{ $isLive ? 1 : 0 }},
        debounce: {{ $debounce }},
        debounceTimer: null,
        init() {
            this.updateDisplay(this.rawValue);
        },
        updateDisplay(value) {
            const locale = '{{ $locale }}';
            if (locale === 'pt-BR') {
                this.displayValue = Money.brlMask(value);
            } else {
                this.displayValue = Money.usdMask(value);
            }
        },
        updateAttribute() {
            if (this.debounceTimer) {
                clearTimeout(this.debounceTimer);
            }

            if (this.isLive && this.debounce > 0) {
                this.debounceTimer = setTimeout(() => {
                    $wire.set(this.wireModel, this.displayValue, this.isLive);
                }, this.debounce);

                return;
            }

            if (this.isBlur) {
                $wire.call('updatedBlurValue', this.wireModel, this.displayValue);
                return;
            }

            $wire.set(this.wireModel, this.displayValue, this.isLive);
        },
        handleInput(event) {
            this.updateDisplay(event.target.value);
            this.updateAttribute();
        }
    }"
    x-effect="updateDisplay(rawValue)"
>
    @php
        // Captura o evento @input customizado do usuário, se existir
        $customInput = $attributes->get('@input');
        $inputEvent  = $customInput
            ? "handleInput(\$event); " . $customInput
            : "handleInput(\$event)";
    @endphp

    @if ($locale === 'pt-BR')
        <x-ui.input
            {{ $attributes->except(['wire:model', '@input']) }}
            x-model="displayValue"
            @input="{{ $inputEvent }}"
            prefix="{{ $prefix ? 'R$' : '' }}"
        />
    @elseif ($locale === 'en-US')
        <x-ui.input
            {{ $attributes->except(['wire:model', '@input']) }}
            x-model="displayValue"
            @input="{{ $inputEvent }}"
            prefix="{{ $prefix ? '$' : '' }}"
        />
    @endif
</div>

@use(Illuminate\Support\HtmlString)
@use(Illuminate\View\ComponentSlot)

@props([
    'id'          => null,
    'label'       => null,
    'placeholder' => null,
    'xs'          => false,
    'sm'          => false,
    'md'          => false,
    'lg'          => false,
    'showError'   => true,
    'icon'        => false,
    'helperText'  => null,
    'hint'        => null,
    'prefix'      => null,
    'suffix'      => null,
    'name'        => null,
    'loading'     => false,
    'parentClass' => null,
    'disabled'    => false,
])

@php
    $name ??= $attributes->wire('model')->value();
    $id = $id ?? $name ?? uniqid();

    $errorId      = $id . '-error';
    $helperTextId = $id . '-helper';

    $describedBy = collect([
        $errors->has($name) ? $errorId : null,
        $helperText ? $helperTextId : null,
    ])->filter()->implode(' ');

    $classes = match (true) {
        $xs     => 'input-xs',
        $md     => 'input-md',
        $lg     => 'input-lg',
        default => 'input-sm h-10!',
    };

    if ($disabled) {
        $classes .= ' bg-gray-100';
    }
@endphp

<div class="flex flex-col gap-1 relative w-full {{ $parentClass }}">
    @if ($label)
        <div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-0">
            <x-ui.input.label :id="$id" :name="$name" :label="$label" :required="$attributes->get('required')" />

            @if ($hint)
                <small class="max-w-xs break-words text-gray-600 sm:ml-2">{{ $hint }}</small>
            @endif
        </div>
    @endif

    <div>
        <div @class([
            'flex items-center h-10!',
            'border border-gray-950/10 rounded-lg focus-within:ring-2 focus-within:ring-primary overflow-hidden' => $prefix || $suffix,
            'border-error!'                                                                                      => $errors->has($name),
            'bg-gray-100!'                                                                                       => $disabled,
        ])>
            @if ($prefix)
                <span
                    wire:loading.class="bg-gray-100!"
                    @class([
                        'flex items-center justify-center p-0! min-w-10 border-r border-r-gray-950/10 text-gray-500 hover:cursor-default',
                        'bg-gray-100' => $disabled,
                        'bg-white'    => !$disabled,
                        $classes,
                    ])
                >
                    {{ $prefix }}
                </span>
            @endif

            <input
                {{ $attributes->wire('model') }}
                {{
                    $attributes->merge([
                        'id'                => $id,
                        'name'              => $name,
                        'type'              => 'text',
                        'placeholder'       => $placeholder ?? $label,
                        'autocomplete'      => 'off',
                        'disabled'          => $disabled,
                        'wire:loading.attr' => 'disabled',
                        'aria-describedby'  => $describedBy ?: null,
                        'aria-invalid'      => $errors->has($name) ? 'true' : null,
                        'aria-required'     => $attributes->get('required') ? 'true' : null,
                    ])->class([
                        'input w-full rounded-lg text-sm font-normal leading-5 focus:ring-2',
                        'input-bordered'          => !$prefix && !$suffix,
                        'rounded-l-none'          => $prefix,
                        'rounded-r-none'          => $suffix,
                        'border-error!'           => $errors->has($name) && !$prefix && !$suffix,
                        'input-xs'                => $xs,
                        'input-sm h-10!'          => $sm || (!$xs && !$md && !$lg),
                        'input-md'                => $md,
                        'input-lg'                => $lg,
                        'focus:pr-10 hover:pr-10' => $icon && $attributes->get('type') === 'number',
                        'no-focus border-none'    => $prefix || $suffix,
                    ])
                }}
            />

            @if ($suffix)
                <span
                    wire:loading.class="bg-gray-100"
                    class="flex items-center justify-center {{ $classes }} p-0! min-w-10
                        border-l border-gray-950/10 text-gray-500 hover:cursor-default"
                >
                    {{ $suffix }}
                </span>
            @endif
        </div>

        @if ($showError)
            @error($name)
                <x-ui.input.error :id="$errorId" :message="$message" />
            @enderror
        @endif

        @if ($helperText)
            <small id="{{ $helperTextId }}" class="wrap-break-word text-gray-600">{{ $helperText }}</small>
        @endif
    </div>
</div>

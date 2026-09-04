@props([
    'id',
    'name' => null,
    'label',
    'required' => false,
])

<label for="{{ $id }}" {{ $attributes }}>
    <span @class([
        'text-gray-950 text-sm font-medium leading-5 relative',
        'text-error' => isset($errors) && $errors->has($name ?? $id),
    ])>
        {{ $label ?? $slot }}

        @if ($required)
            <span class="text-error absolute top-0 -right-2 text-xs"> * </span>
        @endif
    </span>
</label>

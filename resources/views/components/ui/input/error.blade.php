@props([
    'message',
    'id' => null,
])

<small
    @if ($id) id="{{ $id }}" @endif
    role="alert"
    class="label label-alt text-error -mt-1.5 text-wrap"
>{{ $message }}</small>

@props([
    'prefix',
    'oldFile' => false,
])

<div
    x-bind:id="'{{ $prefix }}-file-remove-' + index"
    class="p-1 text-gray-400 hover:cursor-pointer hover:bg-gray-50 hover:text-red-500"
    @click="removeFile(index, {{ $oldFile }})"
>
    <x-icons.x-mark class="size-5" />
</div>

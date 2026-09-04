@props([
    'prefix',
])

<a
    x-bind:id="getPreviewId('{{ $prefix }}', 'video', (typeof index !== 'undefined' ? index : null))"
    :href="file.preview"
    target="_blank"
    rel="noopener noreferrer"
    class="flex size-16 shrink-0 items-center justify-center rounded-md bg-blue-100"
>
    <x-icons.video-camera class="size-9 text-blue-600" />
</a>

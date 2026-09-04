@props([
    'prefix',
])

<a
    x-bind:id="getPreviewId('{{ $prefix }}', 'image', (typeof index !== 'undefined' ? index : null))"
    :href="file.preview"
    target="_blank"
    rel="noopener noreferrer"
    class="size-16 overflow-hidden rounded-lg border border-gray-200 shadow-sm hover:cursor-pointer"
>
    <img :src="file.preview" class="h-full w-full object-cover" />
</a>

@props([
    'loading' => true,
])

<div class="min-w-0 flex-1">
    <p class="truncate text-sm font-medium text-gray-800" x-text="file.name"></p>
    <p
        class="mt-1 text-xs text-gray-500"
        x-text="(file.size / 1024 / 1024).toFixed(2) + 'MB • ' + file.type.split('/').pop().toUpperCase()"
    ></p>

    @if ($loading)
        <div x-show="file.uploaded && file.progress < 100" class="mt-1 h-2 w-full overflow-hidden rounded bg-gray-200">
            <div class="h-2 bg-blue-500" :style="`width: ${file.progress}%`"></div>
        </div>

        <p
            x-show="file.uploaded && file.progress < 100"
            class="mt-1 text-xs text-gray-500"
            x-text="file.progress + '% concluído'"
        ></p>

        <p x-show="file.uploaded && file.progress === 100" class="text-success mt-1 flex items-center gap-1 text-xs">
            <x-icons.check class="text-success size-3" />
            <span class="text-success">Carregamento concluído</span>
        </p>
    @endif
</div>

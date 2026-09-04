@use('App\Enums\AcceptedTypes')

@props([
    'label'       => null,
    'id'          => null,
    'name'        => null,
    'description' => null,
    'accept'      => null,
    'maxSize'     => 10,
    'maxFiles'    => 10,
    'oldFiles'    => [],
])

@php
    $name  = $name ?? $attributes->wire('model')->value();
    $id    = $id ?? $name ?? uniqid();
    $model = $attributes->wire('model')->value();

    $translatedAttribute = trans('validation.attributes.' . $attributes->wire('model')->value());

    $accept = $accept ?? AcceptedTypes::default();

    $translatedFormats = collect(explode(',', $accept))
        ->map(function (string $type) {
            return match (true) {
                str_contains($type, 'image')                                                   => 'Imagens',
                str_contains($type, 'pdf')                                                     => 'PDFs',
                str_contains($type, 'msword'), str_contains($type, 'ms-word')                  => 'DOC',
                str_contains($type, 'openxmlformats-officedocument.wordprocessingml.document') => 'DOCX',
                str_contains($type, 'video')                                                   => 'Vídeos',
                default                                                                        => 'Arquivos',
            };
        })
        ->unique()
        ->join(', ');
@endphp

<div
    {{ $attributes->whereDoesntStartWith('wire:model')->merge(['class' => 'space-y-4']) }}
    x-data="multipleUpload(
        @js($model),
        @js($oldFiles),
        @js($maxFiles),
        @js($maxSize),
        @js($accept),
        @js($translatedAttribute),
        @js($translatedFormats)
    )"
    x-on:livewire-upload-progress.window="handleUploadProgress($event.detail.progress)"
>
    @if (!$attributes->get('disabled'))
        <div
            class="w-full"
            x-on:dragover.prevent="dragging = true"
            x-on:dragleave.prevent="dragging = false"
            x-on:drop.prevent="handleDrop($event.dataTransfer.files)"
        >
            @if ($label || $description)
                <div class="mb-2">
                    @if ($label)
                        <h3 class="text-base font-medium text-slate-800">{{ $label }}</h3>
                    @endif

                    @if ($description)
                        <p class="mt-1 text-xs text-slate-500">{{ $description }}</p>
                    @endif
                </div>
            @endif

            <label
                :class="{ 'ring-2 ring-blue-500 bg-blue-50': dragging }"
                class="block cursor-pointer rounded-lg border-2 border-dashed bg-slate-50 p-6 text-center"
            >
                <input
                    id="{{ $id }}"
                    type="file"
                    multiple
                    accept="{{ $accept }}"
                    {{ $attributes->whereDoesntStartWith('wire:model') }}
                    x-ref="input"
                    class="hidden"
                    @change="addFiles($event.target.files)"
                />

                <div class="flex flex-col items-center justify-center">
                    <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
                        <x-icons.arrow-up-tray class="size-6 text-slate-400" />
                    </div>

                    <p class="mb-1 text-sm text-slate-500">Arraste e solte arquivos aqui</p>
                    <p class="text-xs text-slate-400">ou</p>
                    <span class="mt-2 inline-flex h-9 items-center justify-center gap-2 rounded-md border px-3 text-sm font-medium">Selecionar arquivos</span>
                    <p class="mt-2 text-xs text-slate-400">Formatos aceitos: {{ $translatedFormats }}</p>
                    <p class="text-xs text-slate-400">
                        Tamanho máximo: {{ $maxSize / 1024 }}MB • Máximo de {{ $maxFiles }} arquivos
                    </p>
                </div>
            </label>
        </div>

        @error($model)
            <x-ui.input.error :message="$message" class="mt-2" />
        @enderror

        <x-ui.input.upload.alert-error :model="$model" />
    @else
        <div x-show="oldFiles && oldFiles.length === 0">
            <p class="text-sm text-slate-500">Nenhum arquivo encontrado.</p>
        </div>
    @endif

    <template x-for="(file, index) in oldFiles" :key="file.id">
        <x-ui.input.upload.card prefix="old" :old-file="true" :disabled="$attributes->get('disabled')" />
    </template>

    <template x-for="(file, index) in files" :key="file.key">
        <x-ui.input.upload.card prefix="new" />
    </template>
</div>

@use('App\Enums\AcceptedTypes')

@props([
    'label'       => null,
    'id'          => null,
    'name'        => null,
    'description' => null,
    'accept'      => null,
    'maxSize'     => 10,
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
    x-data="fileUpload(
        @js($model),
        @js($maxSize),
        @js($accept),
        @js($translatedAttribute),
        @js($translatedFormats)
    )"
    x-on:livewire-upload-progress.window="progress = $event.detail.progress"
>
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
            x-show="! file"
            :class="{ 'ring-2 ring-blue-500 bg-blue-50': dragging }"
            class="block cursor-pointer rounded-lg border-2 border-dashed bg-slate-50 p-6 text-center"
        >
            <div class="flex items-center gap-2">
                <div class="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
                    <x-icons.arrow-up-tray class="size-6 text-slate-400" />
                </div>

                <div class="flex flex-col items-start justify-start">
                    <input
                        id="{{ $id }}"
                        type="file"
                        {{ $attributes->whereDoesntStartWith('wire:model')->merge(['class' => 'hidden']) }}
                        accept="{{ $accept }}"
                        x-ref="input"
                        @change="addFile($event.target.files)"
                    />

                    <p class="text-md text-slate-800">Selecione um arquivo</p>

                    <p class="text-xs text-slate-400">
                        Formatos aceitos: {{ $translatedFormats }} (máx. {{ $maxSize / 1024 }}MB)
                    </p>
                </div>
            </div>
        </label>
    </div>

    <template x-if="file">
        <div class="-mt-2 flex items-start space-x-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <template x-if="file?.type.includes('video') || getPreviewMimeTypes('video').includes(file?.type)">
                <x-ui.input.upload.previews.video prefix="new" />
            </template>

            <template x-if="file?.type.includes('pdf') || getPreviewMimeTypes('document').includes(file?.type)">
                <x-ui.input.upload.previews.pdf prefix="new" />
            </template>

            <template x-if="file?.type.includes('image') || getPreviewMimeTypes('image').includes(file?.type)">
                <x-ui.input.upload.previews.image prefix="new" />
            </template>

            <x-ui.input.upload.details />

            <div
                id="remove-file-{{ $id }}"
                class="p-1 text-gray-400 hover:cursor-pointer hover:bg-gray-50 hover:text-red-500"
                @click="removeFile()"
            >
                <x-icons.x-mark class="size-5" />
            </div>
        </div>
    </template>

    @error($model)
        <x-ui.input.error :message="$message" class="mt-2" />
    @enderror

    <x-ui.input.upload.alert-error :model="$model" />
</div>

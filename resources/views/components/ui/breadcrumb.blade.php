@props([
    'items' => [],
])

@if (!empty($items))
    <nav aria-label="Breadcrumb" class="mb-5">
        <ol class="flex items-center gap-1 text-gray-500">
            <li>
                <a id="breadcrumb-home" href="{{ route('home') }}" aria-label="Página inicial">
                    <x-icons.mini.home class="mb-0.5 size-5!" aria-hidden="true" />
                    <span class="sr-only">Página inicial</span>
                </a>
            </li>

            @foreach ($items as $item)
                @php
                    if (is_string($item)) {
                        $item = ['label' => $item];
                    }

                    $isCurrentPage = $loop->last;
                @endphp

                <li class="flex items-center gap-1">
                    <x-icons.mini.chevron-right class="size-5" aria-hidden="true" />

                    @if (isset($item['route']) && !$isCurrentPage)
                        <a
                            href="{{ $item['route'] }}"
                            id="{{ 'breadcrumb-' . str($item['label'])->kebab()->lower() }}"
                            class="text-md font-semibold text-gray-500 hover:text-gray-700"
                        >
                            {{ $item['label'] }}
                        </a>
                    @else
                        <span
                            id="{{ 'breadcrumb-' . str($item['label'])->kebab()->lower() }}"
                            class="text-md font-semibold text-gray-500"
                            @if ($isCurrentPage)
                                aria-current="page"
                            @endif
                        >
                            {{ $item['label'] }}
                        </span>
                    @endif
                </li>
            @endforeach
        </ol>
    </nav>
@endif

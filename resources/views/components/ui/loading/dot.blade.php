@props([
    'activeDot' => 0,
])

<span
    class="bg-primary mt-2 h-1 w-1 rounded-full"
    :class="{ 'translate-y-[-1.5px]': activeDot === {{ $activeDot }} }"
    x-transition:enter="transition ease-out duration-300"
    x-transition:leave="transition ease-in duration-300"
></span>

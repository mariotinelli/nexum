@props([
    'id',
    'active' => false,
])

<div class="bg-white px-6 pt-4 pb-6" data-wizard-step="{{ $id }}" x-show="currentStep === '{{ $id }}'">{{ $slot }}</div>

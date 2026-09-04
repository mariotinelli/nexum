@props([
    'text',
    'label' => null,
])

@php
    $ariaLabel = $label ? "Copiar {$label}" : 'Copiar conteúdo';
@endphp

<button
    type="button"
    class="tooltip flex items-center space-x-2 py-2"
    x-data="{
        text: @js($text),
        copied: false,
        feedbackMessage: '',
        setFeedback(message, copied = false) {
            this.feedbackMessage = message
            this.copied = copied
            setTimeout(() => {
                this.feedbackMessage = ''
                this.copied = false
            }, 1000)
        },
        fallbackCopy(text) {
            const textarea = document.createElement('textarea')
            textarea.value = text
            textarea.setAttribute('readonly', '')
            textarea.style.position = 'absolute'
            textarea.style.left = '-9999px'
            document.body.appendChild(textarea)
            textarea.select()

            const copied = document.execCommand('copy')

            document.body.removeChild(textarea)

            if (! copied) {
                throw new Error('copy-failed')
            }
        },
        async copy() {
            try {
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(this.text)
                } else {
                    this.fallbackCopy(this.text)
                }

                this.setFeedback('Copiado com sucesso!', true)
            } catch {
                this.setFeedback('Não foi possível copiar')
            }
        }
    }"
    x-bind:class="copied ? 'tooltip-info tooltip-open' : ''"
    @click="copy()"
    x-bind:data-tip="feedbackMessage || 'Copiar'"
    aria-label="{{ $ariaLabel }}"
>
    @if ($label)
        <span>{{ $label }}</span>
    @endif

    <x-icons.clipboard class="h-5 w-5" aria-hidden="true" />

    <span class="sr-only" aria-live="polite" role="status" x-text="feedbackMessage"></span>
</button>

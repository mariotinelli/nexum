@php
    $toasts = session()->get('toast');
    session()->forget('toast');
@endphp

<div
    role="status"
    aria-label="Notificações"
    aria-live="polite"
    aria-atomic="true"
    aria-relevant="additions"
    x-data="{
        toasts: [],
        toastNextPage: @js($toasts),
        init() {
            if (this.toastNextPage) {
                this.toastNextPage.forEach((toast) => {
                    this.add(toast);
                });
            }
        },
        add(toast) {
            toast.key = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
            toast.show = false;
            toast.progress = 100;
            this.toasts.push(toast);
            this.play(toast.key);
        },
        remove(key) {
            this.toasts = this.toasts.filter((toast) => toast.key !== key);
        },
        play(key) {
            let toast = this.toasts.find((toast) => toast.key === key);

            if(! toast.persistent) {
                let progressInterval = setInterval(() => {
                    toast.show = true;
                    toast.progress--;
                    if (toast.progress <= 0) {
                        toast.show = false;
                        this.remove(key);
                        clearInterval(progressInterval);
                    }
                }, toast.time * 10);
            } else {
                toast.show = true;
            }
        }
    }"
    @toast.window="add($event.detail)"
    class="pointer-events-none fixed inset-0 z-1000 flex flex-col items-end justify-start space-y-4 px-4 py-6 sm:p-6"
>
    <template x-for="toast in toasts" :key="toast.key">
        <div
            role="alert"
            :aria-label="toast.title"
            x-show="toast.show"
            class="toast-notification pointer-events-auto relative w-full max-w-sm overflow-hidden rounded-xl bg-white pb-0 shadow-lg"
            x-transition:enter="transform ease-out duration-300 transition"
            x-transition:enter-start="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
            x-transition:enter-end="translate-y-0 opacity-100 sm:translate-x-0"
            x-transition:leave="transition ease-in duration-100"
            x-transition:leave-start="opacity-100"
            x-transition:leave-end="opacity-0"
        >
            <div class="border-t-gray-250 border-x-gray-250 flex items-center gap-2 border-x border-t px-4 py-3">
                <x-icons.check-circle
                    class="size-6 min-h-6 min-w-6 text-green-500"
                    x-show="toast.type === 'success'"
                    aria-hidden="true"
                />
                <x-icons.exclamation
                    class="text-warning size-6 min-h-6 min-w-6"
                    x-show="toast.type === 'warning'"
                    aria-hidden="true"
                />
                <x-icons.information-circle
                    class="text-info size-6 min-h-6 min-w-6"
                    x-show="toast.type === 'info'"
                    aria-hidden="true"
                />
                <x-icons.x-circle
                    class="text-error size-6 min-h-6 min-w-6"
                    x-show="toast.type === 'error'"
                    aria-hidden="true"
                />

                <div class="flex flex-col">
                    <span class="text-md font-semibold text-gray-800" x-html="toast.title"></span>
                    <span
                        class="text-sm font-normal text-gray-600"
                        x-show="toast.description"
                        x-html="toast.description"
                    ></span>
                </div>

                <button
                    type="button"
                    @click="remove(toast.key)"
                    class="flex grow justify-end"
                    aria-label="Fechar notificação"
                >
                    <x-icons.x-mark class="h-4 w-4 text-gray-400" aria-hidden="true" />
                </button>
            </div>

            <div
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
                :aria-valuenow="toast.progress"
                class="h-1"
                x-bind:class="{
                    'bg-green-500': toast.type == 'success',
                    'bg-warning': toast.type == 'warning',
                    'bg-error': toast.type == 'error',
                    'bg-info': toast.type == 'info',
                }"
                x-bind:style="`width: ${toast.progress}%;`"
                x-show="! toast.persistent"
            ></div>
        </div>
    </template>
</div>

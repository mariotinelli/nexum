<div
    x-cloak
    id="alert-modal"
    x-data="{
        alerts: [],
        lastFocusedElement: null,
        getFocusableElements(container) {
            return [
                ...container.querySelectorAll(
                    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex=\'-1\'])',
                ),
            ].filter((element) => element.offsetParent !== null);
        },
        focusFirstAction(alertKey) {
            const dialog = this.$el.querySelector(`#info-modal-${alertKey}`);

            if (! dialog) {
                return;
            }

            const focusable = this.getFocusableElements(dialog);
            focusable[0]?.focus();
        },
        trapFocus(event, alertKey) {
            const dialog = this.$el.querySelector(`#info-modal-${alertKey}`);

            if (! dialog) {
                return;
            }

            const focusable = this.getFocusableElements(dialog);

            if (focusable.length === 0) {
                return;
            }

            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();

                return;
            }

            if (! event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        },
        remove(key) {
            this.alerts = this.alerts.filter((alert) => alert.key !== key);

            if (this.alerts.length === 0 && this.lastFocusedElement) {
                this.lastFocusedElement.focus();
            }
        },
        add(alert) {
            this.lastFocusedElement = document.activeElement;
            alert.key = Date.now();
            alert.is_confirmation = alert.type === 'confirmation';
            this.alerts.push(alert);

            this.$nextTick(() => this.focusFirstAction(alert.key));
        },
        call(alert) {
            Livewire.find(alert.componentId).call(alert.method, alert.params);

            this.remove(alert.key);
        },
        callCancel(alert) {
            Livewire.find(alert.componentId).call(alert.actionCancel, alert.params);

            this.remove(alert.key);
        },
    }"
    @alert.window="add($event.detail)"
    class="pointer-events-none fixed inset-0 z-75 flex flex-col items-end justify-center space-y-4 px-4 py-6 sm:justify-start sm:p-6"
    :class="alerts.length ? 'bg-black/50' : null"
>
    <template x-for="alert in alerts" :key="alert.key">
        <dialog
            x-bind:id="'info-modal-' + alert.key"
            class="modal"
            role="dialog"
            aria-modal="true"
            x-bind:aria-labelledby="'alert-modal-title-' + alert.key"
            x-on:keydown.tab="trapFocus($event, alert.key)"
            x-on:keydown.escape.prevent="remove(alert.key)"
            open
        >
            <div class="modal-box pointer-events-auto w-full max-w-xl rounded-md p-0 shadow-lg">
                <div class="flex gap-2 p-6">
                    <x-icons.exclamation-triangle
                        class="text-secondary size-8!"
                        x-show="alert.type !== 'confirmation'"
                    />

                    <div class="flex w-full flex-col gap-4">
                        <h3
                            x-show="alert.title"
                            x-text="alert.title"
                            x-bind:id="'alert-modal-title-' + alert.key"
                            class="text-primary-content-800 text-xl font-bold"
                        ></h3>

                        <p class="text-base-450" x-show="alert.description" x-html="alert.description"></p>
                    </div>
                </div>

                <div class="flex items-center justify-end gap-2 border-t bg-gray-50 p-3">
                    <x-ui.button
                        label="Fechar"
                        ghost
                        class="hover:bg-gray-100"
                        x-show="! alert.is_confirmation"
                        x-on:click="remove(alert.key)"
                    />
                    <x-ui.button
                        x-text="alert.textCancel"
                        ghost
                        class="hover:bg-gray-100"
                        x-show="alert.is_confirmation && alert.textCancel"
                        x-on:click="alert.actionConfirm ? remove(alert.key) : call(alert)"
                    />
                    <x-ui.button
                        x-text="alert.textConfirm"
                        error
                        x-show="alert.is_confirmation && alert.method"
                        x-on:click="
                            alert.actionConfirm && alert.method
                                ? call(alert)
                                : alert.actionCancel
                                  ? callCancel(alert)
                                  : remove(alert.key)
                        "
                    />
                </div>
            </div>
        </dialog>
    </template>
</div>

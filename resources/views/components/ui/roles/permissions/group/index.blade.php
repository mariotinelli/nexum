@use('App\Enums\Can')

@props([
    'header',
    'description',
])

@php
    $model = $attributes->wire('model')->value();
@endphp

<div x-data="{ selectedPermissions: @entangle($model), totalPermissions: 0, checkedAll: false }">
    <x-ui.card
        divided
        :header="$header ?? 'Permissões'"
        :description="$description ?? 'Selecione as permissões que deseja atribuir a este perfil.'"
    >
        <x-slot name="headerAction">
            <x-ui.button
                x-show="! checkedAll"
                id="select-all-permissions"
                primary
                xs
                outline
                icon="check"
                @click="$dispatch('select-all-permissions')"
            >
                Marcar todas
            </x-ui.button>

            <x-ui.button
                x-effect="checkedAll = this.selectedPermissions?.length < this.totalPermissions"
                x-show="checkedAll"
                id="unmark-all-permissions"
                primary
                xs
                outline
                icon="x-mark"
                @click="$dispatch('unmark-all-permissions')"
            >
                Desmarcar todas
            </x-ui.button>
        </x-slot>

        <div class="space-y-4">
            @foreach (Can::groups() as $groupKey => $group)
                @php
                    $permissions = $group->permissions ?? collect($group->group)->pluck('permissions')->flatten()->toArray();
                @endphp

                <div
                    id="{{ "group-{$groupKey}" }}"
                    class="overflow-hidden rounded-lg border"
                    x-ref="group"
                    x-data="{
                        open: false,
                        group: @js($group),
                        permissions: @js($permissions),
                        count: 0,
                        groupSelected: false,
                        model: @js($model),
                        init: function () {
                            this.totalPermissions += this.permissions.length;

                            this.refreshPermissions();

                            this.$watch('selectedPermissions', (value) => {
                                this.checkedAll = value.length === this.totalPermissions;

                                this.syncProperty();
                            });

                            this.$wire.on('select-template', (templatePermissions) => {
                                this.selectedPermissions = [...new Set(...templatePermissions)];
                                this.refreshPermissions();
                            });

                            this.$wire.on('select-all-permissions', () => {
                                this.selectedPermissions = [...new Set(this.selectedPermissions.concat(this.permissions))];
                                this.refreshPermissions();
                            });

                            this.$wire.on('unmark-all-permissions', () => {
                                this.selectedPermissions = this.selectedPermissions.filter(permission => ! this.permissions.includes(permission));
                                this.refreshPermissions();
                            });
                        },
                        get allSelected() {
                            return this.count === this.permissions.length;
                        },
                        refreshPermissions() {
                            this.count = 0;
                             if (this.selectedPermissions.length > 0) {
                                this.permissions.forEach(permission => {
                                    if (this.selectedPermissions.includes(permission)) {
                                        this.count++;
                                    }
                                });
                            }
                        },
                        selectPermission: function (checked, value) {
                            if (checked === true) {
                                const permission = this.permissions.find(permission => permission === value);
                                this.selectedPermissions = [...new Set(this.selectedPermissions.concat(permission))];
                                this.count++;

                                return;
                            }

                            this.groupSelected = false;
                            this.selectedPermissions = this.selectedPermissions.filter(permission => permission !== value);
                            this.count--;
                        },
                        selectGroup: function(checked) {
                            this.groupSelected = checked;

                            if (checked === true) {
                                this.selectedPermissions = [...new Set(this.selectedPermissions.concat(this.permissions))];
                                this.count = this.permissions.length;

                                return;
                            }

                            this.selectedPermissions = this.selectedPermissions.filter(permission => ! this.permissions.includes(permission));
                            this.count = 0;
                        },
                        syncProperty: function() {
                            this.$wire.set(this.model, this.selectedPermissions, false);
                        }
                    }"
                >
                    <x-ui.roles.permissions.group.header :group="$group" :group-key="$groupKey" />

                    <x-ui.roles.permissions.group.content :group="$group" />
                </div>
            @endforeach
        </div>

        @error($model)
            <x-ui.input.error :message="$message" />
        @enderror
    </x-ui.card>
</div>

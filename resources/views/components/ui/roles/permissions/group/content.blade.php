@props([
    'group',
])

<div x-show="open" x-collapse.duration.400ms class="px-6" x-bind:class="{ 'pb-6 pt-4': open }">
    <div class="space-y-3">
        @if ($group->permissions ?? null)
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                @foreach ($group->permissions as $permission)
                    <div class="flex items-start gap-3 space-x-2">
                        <x-ui.input.checkbox
                            :id="$permission->value"
                            sm
                            :label="$permission->label()"
                            :helper-text="$permission->description()"
                            x-bind:checked="groupSelected || selectedPermissions.includes('{{ $permission->value }}')"
                            @change="selectPermission($event.target.checked, '{{ $permission->value }}')"
                        />
                    </div>
                @endforeach
            </div>
        @else
            <div class="space-y-6">
                @foreach ($group->group as $permissionsGroup)
                    <div class="space-y-3">
                        <p class="border-b pb-1 text-sm font-semibold text-gray-600">{{ $permissionsGroup->label }}</p>
                        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                            @foreach ($permissionsGroup->permissions as $permission)
                                <div class="flex items-start gap-3 space-x-2">
                                    <x-ui.input.checkbox
                                        :id="$permission->value"
                                        sm
                                        :label="$permission->label()"
                                        :helper-text="$permission->description()"
                                        x-bind:checked="groupSelected || selectedPermissions.includes('{{ $permission->value }}')"
                                        @change="selectPermission($event.target.checked, '{{ $permission->value }}')"
                                    />
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endforeach
            </div>
        @endif
    </div>
</div>

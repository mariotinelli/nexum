@foreach ($this->groups as $group)
    @if ($group->label)
        <x-ui.sidebar.group :name="$group->label">
            @foreach ($group->items as $item)
                <x-ui.sidebar.link
                    :route="$item->route"
                    :icon="$item->icon"
                    :name="$item->name"
                    :prefix="$item->prefix"
                />
            @endforeach
        </x-ui.sidebar.group>
    @else
        <x-ui.sidebar.links>
            @foreach ($group->items as $item)
                <x-ui.sidebar.link
                    :route="$item->route"
                    :icon="$item->icon"
                    :name="$item->name"
                    :prefix="$item->prefix"
                />
            @endforeach
        </x-ui.sidebar.links>
    @endif
@endforeach

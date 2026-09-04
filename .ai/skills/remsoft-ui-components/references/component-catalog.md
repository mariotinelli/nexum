# x-ui Component Catalog

- [Layout and navigation](#layout-and-navigation)
- [Typography and display](#typography-and-display)
- [Feedback and overlays](#feedback-and-overlays)
- [Actions and navigation widgets](#actions-and-navigation-widgets)
- [Table system](#table-system)
- [Form shell](#form-shell)
- [Input system](#input-system)
- [Modal system](#modal-system)
- [Repeater and wizard](#repeater-and-wizard)
- [Domain components](#domain-components-optional)
- [Quick usage patterns](#quick-usage-patterns)


### Layout and Navigation

#### `x-ui.page`

- Props: `title`, `breadcrumb`, `description=null`, `headerActions=null`, `widgets=null`, `contentClass=null`
- Slots: default, `headerActions`, `widgets`

#### `x-ui.page.header`

- Props: `title`, `description`, `actions=null`

#### `x-ui.page.widgets`

- Sem props

#### `x-ui.breadcrumb`

- Props: `items=[]`
- `items` accepts a string or an array with `label` and optional `route` (URL).

#### `x-ui.navbar`

- Sem props

#### `x-ui.main`

- Sem props

#### `x-ui.sidepage`

- Props: `header=null`, `footer=null`, `description=null`, `sm|md|lg|xl|xl2|xl3|xl4|xl5|xl6|xl7=false`
- Control: uses `@entangle('sidepageOpen').live`

#### `x-ui.sidebar.group`

- Props: `name`, `open=true`

#### `x-ui.sidebar.link`

- Props: `route`, `name`, `icon`, `permission=null`, `prefix=null`

#### `x-ui.sidebar.links`

- Declared props: `route`, `name`, `icon`, `permission` (slot wrapper)

### Typography and Display

#### `x-ui.title`

- Props: `lg=false`, `md=false`, `sm=false`

#### `x-ui.card`

- Props: `header=null`, `description=null`, `divided=null`, `headerAction=null`, `footer=null`, `wizard=false`
- Slots: default, `header`, `headerAction`, `footer`
- Usage pattern: include `divided` on all cards (except when there is visual justification).

#### `x-ui.badge`

- Content props: `label=null`, `icon=null`, `rightIcon=false`
- Size props: `xs|sm|md|lg`
- Color props: `primary|secondary|accent|neutral|info|success|warning|error` or `color='...'`
- Style props: `outline`, `ghost`, `circle`
- Dot: `addDot`, `animateDot`

#### `x-ui.quote`

- Props: `title=null`, colors `neutral|primary|secondary|accent|success|warning|info|error|white`, `color=null`

#### `x-ui.details.card`

- Props: `title`, `value`

#### `x-ui.copy`

- Props: `text`, `label=null`

#### `x-ui.application-logo`

- Props: `purpleHorizontal=false`, `greenHorizontal=false`

#### `x-ui.ilustration`

- Sem props

#### `x-ui.robot`

- Sem props

### Feedback and Overlays

#### `x-ui.alert`

- Props: `title`, `icon=null`, `success|warning|info|error=false`, `color=null`, `soft=false`, `outline=false`, `dash=false`

#### `x-ui.alert-modal`

- Sem props
- Listens to the window `alert` event.

#### `x-ui.toast`

- Sem props
- Consumes session toasts and the `toast` event.

#### `x-ui.loading`

- Sem props

#### `x-ui.loading.dot`

- Props: `activeDot=0`

#### `x-ui.tooltip`

- Props: `label=null`, `open=false`, position `top|bottom|left|right|position`, color `primary|secondary|accent|info|success|warning|error`

### Actions and Navigation Widgets

#### `x-ui.button`

- Label and icon: `label`, `icon`, `rightIcon=false`
- Colors: `neutral|primary|secondary|accent|success|warning|info|error|white`
- Styles: `ghost|link|active|outline|soft|hover|noAnimation`
- Size: `xs|sm|md|lg`
- Shape/layout: `wide|block|circle|square|uppercase`
- State: `loading=null`, `withLoading=true`
- Behavior: `href=false`, `navigate=true`, `inputAction=false`, `cancelButton=false`

#### `x-ui.dropdown`

- Props: `trigger`, `header=null`, `end|top|bottom|left|right=false`, `hover=false`, `open=false`, `sm|md|lg=false`, `width='w-52'`

#### `x-ui.dropdown.link`

- Props: `route`, `name`, `icon`

#### `x-ui.tabs`

- Props: `border|lift|box`, sizes `xs|sm|md|lg|xl`, position `top|bottom`

#### `x-ui.tabs.link`

- Props: `name`, `active=false`, `key='lists_tab'`, `icon=null`

### Table System

#### `x-ui.table`

- Props: `records`, `search=true`, `pagination=true`, `header=null`, `body=null`, `filtersHeader=null`, `filtersDropdown=null`, `tableHeader=null`, `searchInput=null`, `toggleOnlyTrashed=false`
- Slots: `filtersHeader`, `filtersDropdown`, `searchInput`, `tableHeader`, `header`, `body`
- Common Livewire dependencies: `search`, `perPage`, `perPageValues`, `filters`, `sortBy()`, `resetFilters()`.

#### `x-ui.table.th`

- Props: `name=null`, `upperCase=true`, `colspan=null`, `textAlign='left'`, `inline=true`, `withSort=true`

#### `x-ui.table.tr`

- Props: `textAlign='left'`

#### `x-ui.table.td`

- Sem props

#### `components.ui.pagination` (interno)

- No declared `@props`
- May expect pagination context variables (e.g., `recordCount`, `perPageValues`) depending on the local implementation.

### Form Shell

#### `x-ui.form`

- Props: `footer=null`, `cancelRoute=null`

### Input System

#### `x-ui.input`

- Structural props: `id=null`, `name=null`, `label=null`, `placeholder=null`, `parentClass=null`
- Size: `xs|sm|md|lg`
- UX: `showError=true`, `helperText=null`, `hint=null`, `prefix=null`, `suffix=null`, `disabled=false`
- Other: `icon=false`, `loading=false`

#### `x-ui.input.label`

- Props: `id`, `name=null`, `label`, `required=false`

#### `x-ui.input.error`

- Props: `message`

#### `x-ui.input.password`

- No declared props
- `x-ui.input` wrapper with show/hide password toggle.

#### `x-ui.input.textarea`

- Props: `id=null`, `label=null`, `placeholder=null`, `xs|sm|md|lg`, `showError=true`, `maxLength=500`, `hint=null`, `helperText=null`, `parentClass=null`

#### `x-ui.input.checkbox`

- Props: `id=null`, `name=null`, `label=null`, tamanhos `xs|sm|md|lg`, cores `primary|success|warning|error|info`, `showError=true`, `helperText=null`, `inline=true`, `rightLabel=true`

#### `x-ui.input.radio`

- Props: `id=null`, `label=null`, tamanhos `xs|sm|md|lg`, cores `primary|success|warning|error|info`, `showError=true`, `helperText=null`, `inline=true`, `rightLabel=true`

#### `x-ui.input.toggle`

- Props: `id=null`, `label=null`, cores `primary|success|info|warning|error`, `labelRight=false`, `inline=false`, `helperText=null`

#### `x-ui.input.money`

- Props: `locale='pt-BR'`, `prefix=false`
- Accepts `wire:model`, `wire:model.live[.Xms]`, `wire:model.blur`.
- Implemented locales: `pt-BR` and `en-US`.

#### `x-ui.input.datepicker`

- Props in the `App\View\Components\Ui\Input\Datepicker` class:
    - `range=false`, `multiple=false`, `showMonths=1`, `time24hr=true`
    - `minDate=null`, `maxDate=null`, `minTime=null`, `maxTime=null`
    - `date=false`, `time=false`, `datetime=false`, `allowInput=true`
- Automatic formats:
    - `date` -> `d/m/Y`
    - `time` -> `H:i`
    - `datetime` -> `d/m/Y H:i`

#### `x-ui.input.select`

- Props: `name`, `initialValue=null`, `id=null`, `label=null`, `options=[]`, `labeless=false`, `showError=true`, `defaultOptionLabel='Selecione uma opcao'`, `helperText=null`, `hint=null`, `prefix=null`, `suffix=null`, `clearable=true`, `parentClass=null`, `emptyLabel=null`

#### `x-ui.input.select-search`

- Props: `name`, `route`, `withInfinityScroll=true`, `initialValue=null`, `withSearch=true`, `id=null`, `label=null`, `wire=null`, `labeless=false`, `showError=true`, `defaultOptionLabel='Selecione uma opcao'`, `helperText=null`, `hint=null`, `prefix=null`, `suffix=null`, `selectedColumn='id'`, `params=[]`, `parentClass=null`

#### `x-ui.input.multi-select`

- Props: `name`, `initialValue=[]`, `id=null`, `label=null`, `options=[]`, `labeless=false`, `showError=true`, `defaultOptionLabel='Selecione uma ou mais opcoes'`, `helperText=null`, `hint=null`, `prefix=null`, `suffix=null`, `clearable=true`

#### `x-ui.input.multi-select-search`

- Props: `name`, `route`, `withInfinityScroll=true`, `initialValue=[]`, `withSearch=true`, `id=null`, `label=null`, `wire=null`, `labeless=false`, `defaultOptionLabel='Selecione uma ou mais opcoes'`, `showError=true`, `helperText=null`, `hint=null`, `prefix=null`, `suffix=null`, `selectedColumn='id'`, `parentClass=null`

#### `x-ui.input.autocomplete`

- Props: `name`, `route`, `withInfinityScroll=true`, `id=null`, `label=null`, `wire=null`, `labeless=false`, `showError=true`, `helperText=null`, `hint=null`, `prefix=null`, `suffix=null`, `params=[]`

#### `x-ui.input.upload`

- Props: `label=null`, `id=null`, `name=null`, `description=null`, `accept=null`, `maxSize=10`

#### `x-ui.input.multiple-upload`

- Props: `label=null`, `id=null`, `name=null`, `description=null`, `accept=null`, `maxSize=10`, `maxFiles=10`, `oldFiles=[]`

#### Upload internals

- `x-ui.input.upload.card`: `prefix`, `oldFile=false`, `disabled=false`
- `x-ui.input.upload.details`: `loading=true`
- `x-ui.input.upload.remove-button`: `prefix`, `oldFile=false`
- `x-ui.input.upload.alert-error`: `model`
- `x-ui.input.upload.previews.image|pdf|video`: `prefix`

### Modal System

#### `x-ui.modal`

- Props: `id`, `title=''`, `description=''`, `footer=''`, `lg|xl|xl2|xl3=false`, `clickAway=true`, `divided=false`, `headerAlign='left'`, `scrollable=false`, `closeButton=true`, `escapable=true`
- Uses `@entangle('modalOpen')` in the Livewire component.

#### `x-ui.alpine-modal`

- Props: `id=null`, `name=null`, `title=''`, `description=''`, `footer=''`, `lg|xl|xl2=false`, `clickAway=true`, `divided=false`, `headerAlign='left'`
- Event control: `open-modal` and `close-modal`.

### Repeater and Wizard

#### `x-ui.repeater`

- Props: `header=null`, `title=null`, `subtitle=null`, `addButtonText=null`, `addButton=null`, `model=null`, `openAll=true`, `wizard=false`
- Expects Livewire methods: `addItem`, `duplicateItem`, `removeItem`.

#### `x-ui.repeater.item`

- Props: `index`, `itemHeader`, `open=true`, `copyable=true`, `removable=true`
- `@aware`: `model`

#### `x-ui.repeater.item-header`

- Props: `headerActions=null`, `copyable=true`, `removable=true`
- `@aware`: `model`, `index`

#### `x-ui.wizard`

- Props: `header`, `content`, `steps`, `submit='save'`
- Expects Livewire state: `currentStep`, `firstStep`, `lastStep` and methods `prevStep`, `nextStep`.

#### `x-ui.wizard.steps.content`

- Props: `id`, `active=false`

### Domain Components (optional)

#### `x-ui.projects.card`

- Props: `project`

#### `x-ui.projects.tag`

- Props: `tag`, `value`, `tooltip`

#### `x-ui.streets.occupation`

- Props: `occupation`

#### `x-ui.roles.permissions.group`

- Props: `header`, `description`

#### `x-ui.roles.permissions.group.header`

- Props: `group`, `groupKey`

#### `x-ui.roles.permissions.group.content`

- Props: `group`

#### `x-ui.auth-session-status`

- Props: `status`

Note: this section is optional and may vary by product. If a domain component does not exist in the current project, ignore it.

## Quick Usage Patterns

### Button with icon on the right

```blade
<x-ui.button primary icon="check" right-icon>
    Salvar
</x-ui.button>
```

### Select with enum directly in Blade

```blade
<x-ui.input.select
    :options="OrderStatus::options()"
    wire:model="order.status"
    label="Status"
/>
```

### Modal with the project's default footer

```blade
<x-ui.modal id="order-modal" divided title="Editar pedido">
    <div class="py-2">...</div>

    <x-slot name="footer">
        <div class="flex gap-2 bg-gray-100 p-3 items-center justify-end w-full">
            <x-ui.button neutral sm wire:click="closeModal">Fechar</x-ui.button>
            <x-ui.button primary sm wire:click="save">Salvar</x-ui.button>
        </div>
    </x-slot>
</x-ui.modal>
```

### Table with actions in the last column

```blade
<x-slot name="header">
    <x-ui.table.th name="name">Nome</x-ui.table.th>
    <x-ui.table.th></x-ui.table.th>
</x-slot>
```


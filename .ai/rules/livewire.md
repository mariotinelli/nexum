---
paths:
  - 'app/Livewire/**'
---

# Livewire

## Keep Livewire components thin
Livewire components validate, authorize, delegate, and translate results to UI state or feedback. In Brain mode, every mutation must call a Brain Action or Workflow rather than contain business logic.

## Split Livewire CRUD responsibilities
When the operations exist, split a Livewire CRUD into Index, Create, Update, Delete, and Show components. Keep the table and action controls in Index.

## Choose modal or page by form size
Use a modal for a small form. Use a dedicated page when the form is large, has several sections, is multi-step, or needs a stable URL.

## Separate Livewire lifecycle responsibilities
Use mount() for initial loading and access authorization, rules() for validation, and the mutation handler for reauthorization and delegation. Keep render() limited to view construction.

## Namespace and match component events
Name component events as feature::action. The dispatched event name must exactly match its corresponding #[On(...)] listener name.

## Use the established Livewire concern traits
Use WithTable for paginated/filterable/sortable lists, WithModal for modals, WithToast for feedback, WithRepeater for repeaters, WithWizard for multi-step forms, and WithFileUploads for uploads.

## Use separate money and date form state
Never bind x-ui.input.money or x-ui.input.datepicker directly to a model attribute. Use ?string for date state and float|string|null for money state; hydrate it in mount() and copy it into the mutation payload in the handler.

## Allowlist relationship-column sorting
For x-ui.table relationship-column sorting, join the related table, select aliased columns, and map requested sort names through an allowlist to real database columns.

## Validate persisted enums with Rule enum
Validate persisted enum inputs with Rule::enum for the relevant enum class rather than duplicating the allowed values manually.

## Follow the Livewire CRUD event flow
Open Create, Update, and Delete through feature events, confirm deletion in a modal, and dispatch feature::refresh after a successful mutation.

## Call only the multi-step orchestrator
For a dependent multi-step mutation, the Livewire component must call only the Brain Workflow, or the transactional orchestrator Action in Standard mode, rather than coordinating individual steps.

## Dispatch synchronous Brain mutations synchronously
For synchronous UI mutations, call Brain Actions and Workflows with dispatchSync() and a named, explicit payload.

## Do not preload relationship select options
Back relationship selects with paginated search endpoints. Do not load the full related collection into a property or Computed value for options.

## Keep one-off Livewire operations local
A Livewire component may own area-specific behavior such as an admin login or its password-recovery flow when it has no meaningful reuse. Delegate to Brain only when the operation is shared or strongly expected to be shared; reusable user creation remains a Brain Action.

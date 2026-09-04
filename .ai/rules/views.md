---
paths:
  - 'resources/views/**'
---

# Views

## Follow the internal x-ui component contract
Use the remsoft-ui-components conventions whenever creating or editing x-ui.* elements. Reuse existing component APIs and sibling screen patterns.

## Keep table actions on the far right
Place table action columns and controls at the far right by default.

## Use the standard modal presentation
Use divided on x-ui.modal by default. Use a right-aligned modal footer with the established gray background and spacing classes found in sibling modals.

## Do not bind money or date inputs to models
Never bind x-ui.input.money or x-ui.input.datepicker directly to a model attribute. Bind them to the component's separate money or date state property.

## Verify internal component contracts
Treat the local component implementation as the source of truth. Use only declared props, prefer direct flags for boolean props, and omit name or id when wire:model already supplies them.

## Import PHP classes with Blade use
Import PHP classes with @use at the top of Blade files. Avoid inline fully qualified class names in Blade expressions.

## Use Alpine for conditional presentation
Prefer Alpine directives for interaction-driven conditional presentation when viable. Keep critical validation on the backend.

## Use reusable x-ui badge colors
Add unsupported badge colors as generic reusable x-ui.badge options, then render statuses with x-ui.badge and :color instead of inline status classes.

## Pass enum options directly
Pass enum options directly to x-ui selects with options() or toArray(); do not add a Livewire property that only forwards the same options.

## Use searchable selects for relationships
Use x-ui.input.select-search or multi-select-search for relationship fields. Do not use plain select components for relational data unless the user explicitly requests and documents an exception.

## Validate component and HTML attributes
Before using an attribute on x-ui.*, x-icons.*, or an HTML element, verify it on the target implementation or official documentation. Do not infer attribute names by similarity.

## Block invalid relationship select delivery
Do not conclude with a relational field using a plain select or preloaded option collection. Fix it first unless the user explicitly approves and documents an exception.

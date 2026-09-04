---
name: remsoft-brain-addon
description: "Technical guide for r2luna/brain APIs. Use when implementing or reviewing Brain Actions, Workflows, Queries, synchronous dispatch, or Brain pipeline integration."
---

# Remsoft Brain Addon

Use this skill for package-specific syntax and mechanics. Follow the matching project rules for architecture, naming, payloads, HTTP integration, and tests. Local code and project rules prevail on conflict.

## Action reference

```php
/**
 * @property-read array $entityData
 * @property Entity $entity
 */
class CreateEntityAction extends Action
{
    public function rules(): array
    {
        return [
            'entityData.name' => ['required', 'string', 'max:191'],
        ];
    }

    public function handle(): self
    {
        $this->entity = Entity::query()->create([
            'name' => $this->entityData['name'],
        ]);

        return $this;
    }
}
```

## Workflow reference

```php
class CreateEntityWorkflow extends Workflow
{
    protected array $actions = [
        CreateEntityAction::class,
        CreateAvatarAction::class,
        NotifyStakeholdersAction::class,
    ];
}
```

## Synchronous dispatch reference

```php
$action = CreateEntityAction::dispatchSync([
    'entityData' => $entityData,
]);
```

Use `Workflow::dispatchSync([...])` with the same named-payload shape for synchronous multi-step flows.

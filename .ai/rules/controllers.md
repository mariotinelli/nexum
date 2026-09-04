---
paths:
  - 'app/Http/Controllers/**'
---

# Controllers

## Keep controllers thin and delegate mutations
Controllers validate, authorize, delegate, and translate results to HTTP responses. In Brain mode, every web or API mutation must call a Brain Action or Workflow rather than contain business logic.

## Return reusable resources from APIs
Return reusable JsonResource or ResourceCollection objects for successful API responses. Reuse the domain Resource rather than defining endpoint-specific response shapes.

## Call only the multi-step orchestrator
For a dependent multi-step mutation, the controller must call only the Brain Workflow, or the transactional orchestrator Action in Standard mode, rather than coordinating individual steps.

## Dispatch synchronous Brain mutations synchronously
For synchronous HTTP mutations, call Brain Actions and Workflows with dispatchSync() and a named, explicit payload.

## Use invokable single-action controllers
Implement every single-action controller with one public __invoke() method instead of a named action method.

## Delegate reusable controller mutations
Controllers must delegate reusable mutations to Brain, but may keep thin one-off HTTP-specific behavior local when it has no meaningful reuse. Decide by concrete architectural reuse, not by mutation alone.

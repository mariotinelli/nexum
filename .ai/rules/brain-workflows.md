---
paths:
  - 'tests/Feature/Brain/Workflows/**'
---

# Brain Workflows

## Verify orchestration at the Workflow boundary
For a multi-step Brain feature, verify significant action ordering and the final integrated result at the Workflow boundary.

## Execute the real Workflow pipeline
Execute Workflow::dispatchSync() and assert real effects, significant ordering, and the final result. Do not simulate flow coverage by manually calling isolated steps.

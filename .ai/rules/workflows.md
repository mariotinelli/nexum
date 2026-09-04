---
paths:
  - 'app/Brain/Workflows/**'
---

# Workflows

## Use Workflows for dependent mutations
Use a Brain Workflow when multiple dependent mutation steps form one use case. Each independently meaningful mutation remains an Action, and the Workflow owns their orchestration.

## Require ordered multi-action Workflows
Name each Workflow with the Workflow suffix, include at least two Actions, and order them according to their data dependencies.

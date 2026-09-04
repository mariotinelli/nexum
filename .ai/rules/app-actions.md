---
paths:
  - 'app/Actions/**'
---

# App Actions

## Standard-mode application actions
Only in projects without an active Brain structure, use a domain Action for one mutation and a transactional orchestrator Action for dependent multi-step mutations. This project currently uses Brain, so application mutations belong under app/Brain.

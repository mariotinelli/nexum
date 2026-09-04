---
paths:
  - 'app/**'
---

# App

## Treat this project as Brain mode
This project has r2luna/brain and an active Brain structure, so place application logic in Brain Actions, Workflows, and Queries. Reassess the architecture mode before changing this placement convention.

## Pass named explicit application payloads
Pass named, explicit payloads to application-layer Actions, Workflows, Queries, and orchestrators. Avoid ambiguous positional payloads.

## Prefer supported PHP attributes
When Laravel or an installed package supports a PHP attribute for static class configuration, use the attribute instead of the equivalent class property. Confirm the exact attribute and arguments in version-specific documentation.

## Choose Brain for meaningful reuse
Use Brain Actions, Workflows, and Queries when an operation has concrete or strongly likely architectural reuse across entry points or use cases. Do not extract one-off area-specific behavior into Brain merely because it mutates state; theoretical reuse alone is insufficient.

## Brain reuse criterion supersedes blanket placement
The meaningful-reuse criterion supersedes blanket guidance that every mutation must use Brain. Area-specific login and password recovery stay local; user creation uses Brain because multiple entry points share it.

---
paths:
  - 'database/migrations/**'
---

# Migrations

## Use project storage types for money and enums
Store money in cents using unsignedBigInteger. Store integer-backed enum columns using unsignedTinyInteger.

## Keep schema rollouts backward compatible
Prefer backward-compatible migrations. When an immediate schema change could break production compatibility, use a two-step rollout.

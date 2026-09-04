---
paths:
  - '**'
---

# General

## Write pt-BR with correct diacritics
Keep correct accents and cedilla in every Portuguese (pt-BR) text written to project files.

## Optimize images before storing them
Whenever an image is stored in the system, process it with Intervention Image and call `->optimize()` before persisting it. The exact API and processing chain may vary; `$request->image('avatar')->optimize()->store(...)` is only an illustrative example, not a required implementation.

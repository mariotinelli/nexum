---
paths:
  - 'app/Services/**'
---

# Services

## Services are infrastructure boundaries
Use Service classes only for external integrations or infrastructure concerns such as SDK and API calls. Do not place ordinary domain mutations or orchestration in Services.

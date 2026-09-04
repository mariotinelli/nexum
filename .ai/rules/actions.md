---
paths:
  - 'app/Brain/Actions/**'
  - 'app/Brain/**/Actions/**'
---

# Actions

## Use Actions for single mutations
In this Brain-mode project, represent one independently meaningful mutation with one Brain Action. Accept named, explicit payloads rather than ambiguous positional data.

## Validate enum inputs with Rule enum
Validate persisted enum inputs with Rule::enum for the relevant enum class rather than duplicating the allowed values manually.

## Follow the Brain Action contract
Name each Action with a domain verb and the Action suffix. Define rules() for external input, document dynamic payload fields with @property-read, and return self from handle().

## Use Actions for single mutations
Represent one independently meaningful mutation with one Brain Action. Accept named, explicit payloads rather than ambiguous positional data.

## Validate enum inputs with Rule enum
Validate persisted enum inputs with Rule::enum for the relevant enum class rather than duplicating allowed values manually.

## Follow the Brain Action contract
Name each Action with a domain verb and the Action suffix. Define rules() for external input, document dynamic payload fields with @property-read, and return self from handle().

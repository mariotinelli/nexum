# Fatiamento de <Feature>

## Prévia numerada

1. `<título DEV preservando o nome pai>` — `<estimativa>h`
   - Entrega: comportamento observável.
   - Bloqueado por: números anteriores ou nenhum.
   - Bloqueios externos: slice específico; ou Feature provisória, capacidade e motivo explícito; ou nenhum.

## Cobertura

| Regra ou critério | Destino | Evidência |
| --- | --- | --- |
| `<id>: <resumo>` | Slice 1 / existente / outra Feature | `<evidência>` |

## Descrições completas

### 1. <título>

#### Entrega

<resultado humano e verificável>

#### Escopo e limites

<incluído e excluído>

#### Critérios de aceite

- Sucesso: <resultado observável>.
- Erro: <tratamento observável>.
- Permissão: <regra observável, quando relevante>.

#### Dependências

<capacidades que realmente impedem o início, ou nenhuma>

#### Rastreabilidade

Feature Redmine `<id>`; regras/critérios `<ids>`.

Inclua `Contexto técnico` antes da rastreabilidade somente quando uma decisão aprovada exigir esse contexto; omita a seção nos demais casos.

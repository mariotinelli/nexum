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

<contexto funcional comprovado, quando relevante; mudança esperada e comportamento a preservar>

#### Escopo e limites

<fronteiras necessárias para esclarecer a responsabilidade desta tarefa>

#### Critérios de aceite

- <condição e resultado observável de um comportamento>.
- <outro cenário verificável, preservando as condições do requisito>.

#### Dependências

<capacidade e tarefa responsável; distinguir bloqueio de início de integração para conclusão; usar nome e link confirmado quando disponível>

#### Referências

Feature Redmine `<id>`; regras/critérios `<ids>`.

Inclua `Contexto técnico` antes das referências somente quando uma decisão aprovada exigir esse contexto; omita a seção nos demais casos. Aplique a [disciplina de escrita](../../vertical-slicing/references/task-writing.md) antes de apresentar a descrição.

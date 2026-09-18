# Revisão de mudança do requisito

Use esta fase quando o item pai aprovado atual não tiver o mesmo SHA-256 do requisito que fundamentou a publicação concluída. Leia primeiro a [disciplina de mudança semântica](../../vertical-slicing/references/semantic-changes.md). O fluxo registra a análise e a decisão; não implementa a política geral de atualizar ou remover tarefas.

## Preparar o plano

Confirme que `slices-state.json` está aprovado, `slices-publication.json` está concluído e ambos carregam o mesmo `semantic_baseline`. Leia o requisito atual e sua aprovação pelo contrato do `project-flow`. Monte `.work/slices-change-review-plan.json` com `classification`, `summary`, `changes` e `impact`. Cada mudança traz `id`, `classification`, `before`, `after` e `rationale`. O impacto contém listas `affected_*` e `unaffected_*` para `tasks`, `acceptance_criteria`, `coverage` e `dependencies`; cada item possui `id` e `reason`, e o conjunto precisa particionar integralmente o baseline.

Execute:

```sh
python <project-slices>/scripts/manage_change_review.py prepare .flow/slices-change-review.json .work/slices-change-review-plan.json --slices-state .flow/slices-state.json --publication-state .flow/slices-publication.json --current-requirement feature.md --preview slices/change-review.md --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo>"
```

O helper deriva uma identidade estável do pai e das duas versões, inclui evidências de preservação das filhas publicadas, decisões de adoção/externalidade, Studies, divergências e dependências, e reutiliza a mesma revisão numa retomada idêntica. Mostre a prévia completa; ela separa impactos localizados dos itens ainda válidos.

Cada versão do requisito e sua aprovação possuem cópias imutáveis; somente a revisão corrente exige correspondência com os arquivos atuais. Mudanças posteriores acrescentam revisões sem apagar decisões anteriores. Após uma aplicação concluída, inclua no impacto também as filhas e relações criadas por ela.

**Concluído quando:** a comparação semântica cobre todas as diferenças e todo item do baseline aparece exatamente uma vez como afetado ou não afetado, com prévia legível e hashes íntegros.

## Decidir

Somente o tech lead da aprovação do fatiamento decide. Registre `approved` ou `rejected`:

```sh
python <project-slices>/scripts/manage_change_review.py decide .flow/slices-change-review.json --decision approved --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo>"
```

Enquanto a revisão estiver pendente ou rejeitada, mantenha publicação, IDs, aprovações e todo histórico intactos. Mudança editorial aprovada fica registrada e não invalida filhas nem exige refatiamento.

**Concluído quando:** uma decisão única referencia o hash corrente da classificação e do impacto; estados pendente ou rejeitado não alteraram nenhum artefato publicado.

## Liberar somente o conteúdo afetado

Para mudança funcional aprovada, peça ao helper a autorização local das keys afetadas antes de preparar qualquer mutação:

```sh
python <project-slices>/scripts/manage_change_review.py authorize .flow/slices-change-review.json --keys "dev-1" --at "<ISO-8601>"
```

O comando falha diante de baseline, requisito, classificação, impacto ou aprovação alterados; em retomada, reutiliza a autorização sem duplicá-la. Ele não chama o MCP nem atualiza/remove tarefas. Prepare depois novas revisões e aprovações vinculadas somente ao conteúdo afetado, preservando IDs e evidências dos itens não afetados.

**Concluído quando:** a autorização referencia a revisão semântica aprovada, contém somente keys afetadas e nenhuma operação remota foi criada por esta fase.

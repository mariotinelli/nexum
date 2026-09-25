# Contrato do planejamento

## Elegibilidade e alinhamento

Planeje somente uma `tasks/dev-<id>-<slug>/task.md` materializada por uma publicação `project-slices` concluída ou por sua reconciliação legada concluída. QA, Study, filha mantida como externa, origem ausente e identidades divergentes são inelegíveis. O status operacional da filha e do pai é informativo e não participa dessa decisão.

Leia pai e filha pelo MCP Redmine e grave temporariamente somente `parent` e `child` conforme `schemas/redmine-readback.schema.json`. O helper compara ID, tipo, tracker, projeto, pai, título e descrição entre `task.md`, diretório pai, origem estruturada e readback. Divergência interrompe o fluxo, preserva todas as fontes e relata a evidência conflitante; este pacote nunca escreve no Redmine nem escolhe automaticamente uma fonte vencedora.

```sh
python <plan-issue>/scripts/manage_plan.py prepare <repo> <dev-id> --state <dev>/.flow/plan-issue.json --inspection-manifest <temporário.json> --inspected-commit <sha> --origin-state <origem.json> --remote-readback <temporário.json>
```

O manifesto usa exatamente `instructions`, `architecture`, `adrs`, `conventions`, `automations` e `tests`, com listas não vazias de caminhos internos ao repositório. O estado conserva somente caminhos, hashes, identidades, evidência sanitizada e histórico de decisões.

## Baseline e autoridade

```sh
python <plan-issue>/scripts/manage_plan.py baseline <estado> --command "<suíte canônica>" --started-at "<ISO-8601>" --finished-at "<ISO-8601>"
python <plan-issue>/scripts/manage_plan.py approve-baseline <estado> --actor "<desenvolvedor>" --at "<ISO-8601>"
```

Cada baseline registra comando sanitizado, commit inspecionado, duração, resultado, código de saída e todas as linhas normalizadas sanitizadas, sem truncar linhas ou descartar o início da saída. A saída bruta fica em arquivo temporário apagado ao final. Um baseline verde é aceito diretamente; um vermelho bloqueia `record` até `approve-baseline` ligar a decisão explícita do desenvolvedor ao hash exato da evidência.

Mudança no código, requisito, `task.md` ou qualquer fonte inspecionada torna a evidência obsoleta e invalida toda autoridade de execução. Rode nova inspeção e novo baseline. O commit manual do plano pode avançar o HEAD mantendo o código inspecionado e sua ancestralidade. Uma edição de `planning.md` invalida sua aprovação de hash, mas entra no histórico somente por `record`.

## Estrutura de `planning.md`

Use exatamente estas seções de segundo nível, com conteúdo concreto: `Identidade e fontes`, `Objetivo`, `Estado atual`, `Escopo`, `Arquitetura`, `Estratégia`, `Baseline` e `Riscos`.

Depois delas, escreva fases como `## Fase N — <nome>`. Cada fase contém exatamente `Objetivo`, `Dependências`, `Mudanças esperadas`, `Arquivos prováveis`, `Limites`, `Estratégia`, `Aceite` e `Verificação focada` como subtítulos de terceiro nível. Uma fase cabe numa sessão nova, termina em estado seguro para commit e possui aceitação executável.

```sh
python <plan-issue>/scripts/manage_plan.py record <estado> <dev>/planning.md --at "<ISO-8601>" --reason "<motivo>"
python <plan-issue>/scripts/manage_plan.py approve <estado> --actor "<desenvolvedor>" --at "<ISO-8601>"
python <plan-issue>/scripts/manage_plan.py handoff <estado>
```

O desenvolvedor realiza o commit de `planning.md` e da regra de `.gitignore` manualmente. `prepare` mantém `/.flow/` ignorado na pasta da filha: estado e relatórios operacionais ficam locais e não entram nos commits de fase. Se o estado já estiver versionado, preserve o arquivo e remova-o somente do índice Git antes da execução. `handoff` emite o comando exato somente quando baseline, evidência e hash do plano ainda conferem.

## Replanejamento append-only

`record` acrescenta uma revisão; nunca substitui revisões ou aprovações anteriores. Fases concluídas permanecem byte a byte, números retirados ficam aposentados e fases novas continuam depois do maior número histórico. Fases pendentes podem ser revisadas ou retiradas antes da execução.

Depois de fases executadas pelo Ralph, inspecione novamente o projeto e rode `prepare` com o HEAD atual, seguido de um novo `baseline`. A atualização arquiva a evidência anterior e preserva revisões, aprovações e commits concluídos. Resolva qualquer fase ativa ou incerta antes dessa atualização. Use a origem de aplicação concluída quando a filha tiver sido revisada; o helper confere a cadeia de hashes desde a publicação até o `task.md` atual.

Obtenha aprovação explícita do impacto no trabalho pendente antes de registrar a revisão. O estado produzido pelo Ralph já registra as fases concluídas; `observe-execution` serve somente para registrar observações que ainda não constam nele:

```sh
python <plan-issue>/scripts/manage_plan.py observe-execution <estado> --at "<ISO-8601>" --completed-phase <N>
python <plan-issue>/scripts/manage_plan.py approve-impact <estado> --actor "<desenvolvedor>" --at "<ISO-8601>" --impact "<impacto>"
python <plan-issue>/scripts/manage_plan.py record <estado> <dev>/planning.md --at "<ISO-8601>" --reason "<motivo>"
```

Esses comandos registram evidência e decisão; não executam fases nem implementam gates do Ralph.

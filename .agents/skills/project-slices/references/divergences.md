# Divergências materiais e alinhamento do pai

Use esta fase quando a inspeção encontrar diferença material entre o requisito pai aprovado, a proposta de filhas e a descrição que seria publicada. Uma API nova é sempre material quando o requisito aprovado não promete uma API consumível. O tech lead decide sozinho; ele pode consultar o dono do requisito, mas o fluxo não cria segundo aprovador nem gate de QA.

## Preparar a correção exata

Grave em `.work/slices-divergence-plan.json` o documento canônico corrigido proposto, o snapshot sanitizado e fresco do pai, a proposta de slices que revelou a diferença, cada divergência com significado aprovado, correção proposta, impacto e todas as filhas afetadas, além do efeito na publicação. Execute:

```sh
python <project-slices>/scripts/manage_divergence.py prepare .flow/slices-divergence.json .work/slices-divergence-plan.json --feature-dir . --preview slices/divergence.md --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo>"
```

Mostre `slices/divergence.md` integralmente. A prévia contém o delta funcional, as filhas afetadas e a descrição remota resultante, preservando o conteúdo externo aos delimitadores, status e relações do baseline.

**Concluído quando:** cada diferença material possui correção e impacto específicos, a cobertura das filhas afetadas é exata e o hash apresentado liga fontes, baseline, correção e payload remoto.

## Decidir

Registre `decide --decision rejected` ou `decide --decision approved` com ator, instante e motivo. Rejeição preserva os bytes do requisito e do pai e mantém a publicação afetada bloqueada. Aprovação autoriza somente a correção e o payload ligados ao hash corrente.

**Concluído quando:** existe exatamente uma decisão do tech lead para a revisão corrente; nenhuma consulta opcional virou outro gate.

## Alinhar local e remoto

Após aprovação, execute `apply-local`. O helper invalida a aprovação anterior, acrescenta a nova aprovação do requisito e substitui documento, estado e registro de alinhamento como uma transação local. Depois execute `begin-update`, envie apenas seu payload a `redmine_update_issue`, registre o resultado com `finish-update` e sempre faça readback com `observe-update`.

Resultado incerto exige leitura. `matched` conclui sem nova escrita; `baseline` prova ausência e libera retry do mesmo payload. Qualquer terceira descrição, mudança de status, relações, assunto, fonte, evidência ou aprovação bloqueia. Operação concluída nunca volta ao MCP.

**Concluído quando:** o requisito local corrigido tem nova aprovação válida, o pai remoto corresponde exatamente ao payload aprovado, status e relações permanecem iguais ao baseline e o histórico registra tentativas e evidências sem reescrita.

## Retomar as filhas

Rode novamente `check-input`, reconstrua a proposta com o novo hash e obtenha as aprovações ordinárias de decomposição e publicação. Aprovações anteriores ao alinhamento não autorizam filhas alteradas. Estudos, filhas adotadas e externas permanecem como história e seguem seus contratos existentes.

**Concluído quando:** proposta, input check e as duas aprovações ordinárias referenciam a fonte corrigida; nenhuma filha afetada usa autoridade anterior.

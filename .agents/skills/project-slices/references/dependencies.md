# Dependências externas e refinamento

Use esta fase quando um slice DEV só pode começar depois de uma capacidade entregue por outra Feature. Ela configura bloqueios; não declara que a capacidade já foi implementada. Relações Feature→Feature publicadas pelo `project-flow` permanecem sob responsabilidade daquele fluxo e entram apenas como evidência do grafo.

## Registrar no fatiamento

Para cada capacidade que realmente impede iniciar um DEV, preencha `external_blockers` com chave estável, Feature fornecedora, capacidade, motivo e, quando já publicada, a issue do slice específico. Consulte a Feature externa e suas filhas pelo MCP antes de propor: havendo filhas, selecione somente as que entregam a capacidade; sem filhas, deixe os campos de slice nulos e proponha o pai como bloqueador provisório. Não replique a implementação da capacidade no slice dependente.

**Concluído quando:** cada bloqueio impede de fato o início, tem um único dono da capacidade e a proposta usa slices disponíveis ou traz motivo explícito para a aresta provisória.

## Preparar e aprovar relações

Depois do readback da publicação das filhas dependentes, leia pelo MCP todas as issues e relações do grafo de bloqueios relevante. Salve em `.work` um snapshot sanitizado com `scope: "relevant-blocking-graph"`, `complete: true`, projeto, issues (`id`, `parent_issue_id`, `title`) e relações nativas. O snapshot inclui relações fora deste fluxo para detectar ciclos e preservá-las.

Colete o grafo percorrendo pelo MCP as relações alcançáveis de cada endpoint e as filhas de cada Feature fornecedora, até que nenhuma issue nova apareça; somente então marque `complete: true`. Monte `.work/slices-dependencies-plan.json` com `graph_snapshot` e `changes`. Cada mudança informa `key`, `action`, `dependency_key`, `source_issue_id`, `target_key` e `relation_id` (`null` em adição). Prepare a prévia:

```sh
python <project-slices>/scripts/manage_dependencies.py prepare .flow/slices-dependencies.json .work/slices-dependencies-plan.json --slices-state .flow/slices-state.json --publication-state .flow/slices-publication.json --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo>"
```

Mostre ao tech lead o delta, a cobertura e o hash retornado. Somente depois da confirmação explícita execute:

```sh
python <project-slices>/scripts/manage_dependencies.py approve .flow/slices-dependencies.json --actor "<tech lead>" --at "<ISO-8601>"
```

Apresente o hash, a cobertura integral e o delta exato. Uma correção anterior à primeira operação vira nova revisão append-only e invalida a aprovação anterior. Somente o tech lead aprova; mudança no plano, fontes ou grafo exige nova prévia e aprovação.

**Concluído quando:** a revisão corrente cobre todo `external_blockers`, permanece acíclica no grafo completo e possui aprovação válida ligada ao hash atual.

## Aplicar e retomar

Para cada mudança rode `begin` antes do MCP e `finish` depois. `begin` retorna o tool e payload exatos: adições usam `redmine_create_relation`; remoções usam `redmine_delete_relation` com o ID nativo. Em refinamento, conclua e confira todas as relações específicas antes de remover a provisória. O helper aceita remoção somente da relação provisória exata criada e reconciliada por este estado; relações de pais ou de terceiros permanecem intactas.

```sh
python <project-slices>/scripts/manage_dependencies.py begin .flow/slices-dependencies.json --key "<mudança>" --at "<ISO-8601>"
python <project-slices>/scripts/manage_dependencies.py finish .flow/slices-dependencies.json --key "<mudança>" --attempt <n> --outcome completed --relation-id <id-apenas-para-add> --at "<ISO-8601>"
```

Resultado `unknown` ou processo interrompido exige nova leitura completa e `observe` antes de repetir. Para add, `matched` conclui e `absent` libera retry; para remove, `absent` conclui e `matched` libera retry. Divergência para no tech lead.

**Concluído quando:** todas as operações do delta aprovado estão reconciliadas, tentativas e observações permanecem append-only e nenhuma chamada ambígua é repetida sem leitura.

## Conferir

Releia o grafo completo, grave o snapshot em `.work` e execute `complete --readback`. O helper exige todas as novas arestas, ausência da provisória exata removida, preservação de cada relação inicial não afetada e grafo acíclico. `manage_scope` mantém a Feature como fatiada e publicada, mas mostra `dependency_status` separado: `pending`, `refining` ou `ready`. `ready` significa somente relações configuradas e conferidas, não capacidade implementada nem liberação automática do trabalho.

**Concluído quando:** o estado está `completed`, o readback e seu hash são duráveis no histórico, e a liberação de implementação continua sendo uma decisão baseada no estado real das capacidades.

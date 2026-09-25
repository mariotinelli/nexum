# Publicação DEV e QA

Use esta fase somente depois de a decomposição corrente estar `approved`. O helper local guarda intenção e evidência; o agente executa leituras e mutações exclusivamente pelos tools do MCP Redmine.

## Confirmar campos

Se o item pai possuir filhas, conclua primeiro a revisão de [filhas existentes e caminho somente QA](existing-children.md). `prepare` recusa uma lista não vazia sem decisões completas.

Leia novamente o item pai com filhos e relações e consulte projeto, trackers, status e prioridades. Derive esses campos sem perguntar ao tech lead: QA usa sempre o tracker nativo `Deliverable`; DEV usa `Task` quando a mãe usa `Feature` e `Bug` quando a mãe usa `Bug`; o status inicial é sempre `New`; a prioridade inicial é sempre `Normal`. Resolva os IDs pelos nomes no catálogo nativo e interrompa se algum estiver ausente ou ambíguo. Use o mesmo `project_id` e `parent_issue_id` nativo da mãe; herde `category_id` e `fixed_version_id` quando existirem no pai. Deixe responsável, início e vencimento vazios. Envie explicitamente o `priority_id` de `Normal` e não aceite override. Grave a estimativa em `estimated_hours`.

Salve a resposta sanitizada do item pai em `.work/slices-publication-parent.json` e monte `.work/slices-publication-plan.json` com:

```json
{
  "source": {"slices_state_path": "<caminho absoluto>", "slices_state_sha256": "<sha256>"},
  "parent_snapshot": "<caminho absoluto>",
  "metadata_snapshot": "<caminho absoluto com trackers, statuses e priorities>",
  "native_fields": {
    "project_id": 7,
    "dev_tracker_id": 2,
    "qa_tracker_id": 7,
    "initial_status_id": 1,
    "default_priority_id": 4,
    "priority_override_id": null,
    "priority_override_reason": null
  },
  "qa": {
    "title": "[QA] <título completo do item pai>",
    "estimate_hours": 9,
    "blocked_by": ["dev-1"],
    "description": {
      "objective": "...",
      "integrated_journeys": ["..."],
      "rules_permissions": ["..."],
      "related_impacts": ["..."],
      "completion_criteria": ["..."],
      "requirement_references": ["R1"]
    }
  }
}
```

Há exatamente uma QA por item pai. O título é `[QA]` seguido do título completo da Feature ou Bug, sem sufixo. Sua estimativa é própria e não usa a referência de seis horas das DEV. A descrição cobre objetivo, jornadas integradas, regras e permissões, impactos relacionados e critérios de conclusão; referencia os requisitos sem copiar as DEV integralmente. `blocked_by` contém todas e somente as DEV necessárias para liberar a verificação integrada. Ele fica vazio somente quando a decomposição aprovada possui slices vazio e cobertura `existing` integral.

A QA verifica o item pai completo, incluindo os comportamentos classificados como `existing`. Traduza esses cenários em jornadas e critérios verificáveis, preservando as condições do requisito aprovado; a classificação dispensa trabalho DEV, mas não a verificação integrada.

Escreva `objective` como um objetivo curto. Em `integrated_journeys`, separe cenários por comportamento e informe junto de cada cenário a preparação necessária: perfis, dados, dispositivos e condições de sessão ou tempo. Use `rules_permissions` para restrições relevantes e `related_impacts` para comportamentos relacionados que precisam ser preservados, sem repetir as jornadas. Em `completion_criteria`, explique os resultados e evidências necessários para concluir e como registrar impedimentos. Mantenha estimativas em seu campo próprio e decisões administrativas no estado do fluxo.

Exemplo de separação: em vez de reunir todo o ciclo de Lembrar-me em um item, descreva o retorno pelo mesmo navegador dentro de 30 dias e, em outro item, o retorno após o prazo sem sessão válida, incluindo que acessos intermediários não prorrogam a lembrança. Preserve também os demais cenários aprovados, inclusive saída e desativação; o exemplo não substitui a cobertura completa.

**Concluído quando:** identidade do pai, trackers derivados, status inicial, prioridade, heranças, estimativas e bloqueios QA estão explícitos no plano sanitizado, a QA cobre também o comportamento existente e nenhuma credencial foi persistida.

## Prévia e aprovação final

O título da filha pertence ao campo `subject` do Redmine. A descrição começa diretamente em `Entrega` para DEV, `Objetivo` para QA ou `Pergunta técnica` para Study, sem repetir o título. Na prévia agrupada, identifique cada filha fora do corpo da descrição.

Aplique a [revisão editorial](../../vertical-slicing/references/task-writing.md) também à QA, preservando suas jornadas e condições de conclusão. DEV usa “Critérios de aceite”; QA usa “Critérios de conclusão”. A geração apresenta os critérios DEV sem os rótulos internos de classificação. Referências identificam o pai e os requisitos cobertos. Novas renderizações não reescrevem descrições armazenadas em publicações anteriores nem seus hashes; alterações de conteúdo aprovado seguem uma nova revisão e aprovação.

Execute:

```sh
python <project-slices>/scripts/manage_publication.py prepare .flow/slices-publication.json .work/slices-publication-plan.json --slices-state .flow/slices-state.json --preview slices/publication.md --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo>"
```

O helper deriva cada DEV da revisão aprovada. O título DEV é `[DEV]` seguido do título completo do item pai e do sufixo aprovado; uma entrega de API externa pode conter `[API]` depois de `[WEB]`. A prévia conjunta em `slices/publication.md` mostra o conteúdo integral, campos e hashes; as chaves `dev-N` e `qa` permanecem restritas ao estado interno de preparação e retomada.

Mostre essa prévia ao tech lead. Revisões antes da publicação são append-only e invalidam a aprovação final anterior. Depois da confirmação explícita, execute `approve` e preserve uma cópia anterior para `validate --previous`:

```sh
python <project-slices>/scripts/manage_publication.py approve .flow/slices-publication.json --actor "<tech lead>" --at "<ISO-8601>"
python <project-slices>/scripts/manage_publication.py validate .flow/slices-publication.json --previous <estado-anterior.json>
```

**Concluído quando:** a aprovação final válida referencia o `publication_sha256` corrente e nenhuma mutação remota começou antes dela.

## Publicar e retomar

Uma filha adotada conserva o ID e o baseline aprovados e nunca passa por `begin-create`; somente filhas com origem `create` chegam ao MCP de criação.

Para cada filha nova ainda sem operação `create:*` concluída, rode `begin-create` antes do MCP. Ele persiste a intenção `in-flight` e retorna exatamente `attributes`; envie esse objeto a `redmine_create_issue`. Em seguida, rode `finish-create` para registrar `completed`, `failed` ou `unknown`. Se o processo cair entre o início e o resultado, trate `in-flight` como incerto. Mensagens de erro persistidas são sanitizadas.

```sh
python <project-slices>/scripts/manage_publication.py begin-create .flow/slices-publication.json --key dev-1 --at "<ISO-8601>"
python <project-slices>/scripts/manage_publication.py finish-create .flow/slices-publication.json --key dev-1 --attempt 1 --outcome completed --issue-id 501 --at "<ISO-8601>"
```

Um resultado `unknown` ou `in-flight` exige busca pela identidade estável `project-slices-child` no projeto e pai confirmados, abrangendo issues abertas e fechadas. Percorra todas as páginas e grave projeto, pai, identidade, escopo `all`, cada página (`offset`, `limit`, `count`), total e candidatos no snapshot sanitizado. Use `observe-create --outcome matched` somente para um candidato integralmente idêntico; use `absent` somente quando a busca completa não trouxer a identidade. Ambiguidade ou divergência para e volta ao tech lead. Uma operação `completed` nunca volta ao MCP de criação.

Depois que os IDs necessários existem, preserve também os bloqueios DEV da decomposição: em toda relação, a dependência é `issue_id`, a dependente é `issue_to_id` e `relation_type` é `blocks`. Para relações entre filhas novas, rode `begin-relation` antes do MCP e `finish-relation` depois da resposta; um resultado incerto exige leitura de relações e `observe-relation` antes de qualquer repetição. Uma relação que toca filha adotada nunca gera payload: os dois extremos devem ter sido adotados e a relação equivalente deve estar no snapshot aprovado e no readback final.

Falha parcial preserva todos os IDs e relações confirmados. Em retomada, valide o estado, reconcilie primeiro cada `unknown` e continue somente operações pendentes.

**Concluído quando:** cada `create:*` e `relation:*` de filhas novas está reconciliada como concluída uma única vez, relações adotadas possuem evidência completa sem operação de mutação e tentativas e observações permanecem append-only.

## Conferir e concluir

Inclua no readback todas as filhas gerenciadas e todas as descobertas que o tech lead manteve fora. O helper confere o baseline das adotadas, o plano das novas e o fingerprint contratual das externas sem hashear campos voláteis como journals ou attachments.

Leia o item pai e todas as filhas com relações. Salve `.work/slices-publication-readback.json` como `{"parent": {...}, "children": [...]}` e execute `complete`. O helper compara projeto, parentesco, tracker, status inicial, prioridade efetiva, categoria, versão, responsável, datas, estimativa, título, descrição e todos os bloqueios `blocks`. Ele também exige que ID e nome do status do item pai sejam iguais ao baseline.

```sh
python <project-slices>/scripts/manage_publication.py complete .flow/slices-publication.json --readback .work/slices-publication-readback.json --at "<ISO-8601>"
```

Depois de conferir integralmente IDs, conteúdo, tracker, estimativa, pai e relações, o helper grava na mesma transação o estado concluído e uma representação humana estável por filha: `tasks/dev-<id>-<slug>/task.md` ou `tasks/qa-<id>-<slug>/task.md`. O `task.md` contém somente identidade, tipo, tracker, pai, estimativa, descrição e relações; status, responsável e datas operacionais permanecem no Redmine. A primeira materialização fixa o slug: uma releitura posterior reutiliza a pasta encontrada pelo tipo e ID. Estados históricos com `slices/descriptions/` continuam válidos, mas publicações novas não criam nem persistem esses artefatos posicionais.

O fluxo preserva a Feature ou Bug pai. QA é uma filha de verificação e não aprova decomposição, conteúdo ou conclusão.

**Concluído quando:** `slices-publication.json` está `completed`, contém o hash do readback e os hashes de todos os `task.md`, e preserva o histórico completo de revisão, aprovação, IDs, tentativas, observações e progresso. Qualquer falha ou incerteza anterior mantém somente o estado retomável, sem uma árvore canônica definitiva.

Se a decomposição aprovada contém `external_blockers`, continue em [dependências externas e refinamento](dependencies.md). Essa fase acrescenta ou refina relações sem alterar esta publicação concluída nem recriar suas filhas.

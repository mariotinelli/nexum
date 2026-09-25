# Entrada e persistência local

## Layout

Preserve o layout canônico do `project-flow`: `feature.md` ou `bug.md` continua sendo o único documento de requisito na raiz do item pai. Use:

- `.work/slices-remote.json` para o snapshot sanitizado e descartável da leitura Redmine;
- `.flow/slices-input-check.json` para a evidência durável da conferência funcional;
- `.work/slices-proposal.json` para a proposta corrente antes de registrá-la;
- `.work/slices-existing-children.json` para a paginação sanitizada e descartável das filhas preexistentes;
- `.flow/slices-state.json` para revisões, hashes e aprovações duráveis;
- `.flow/slices-divergence.json` para correções materiais, decisão do tech lead, alinhamentos local/remoto, tentativas e readback;
- `.flow/slices-change-review.json` para a comparação semântica append-only entre o requisito atual e o baseline publicado;
- `.flow/slices-revision-application.json` para o delta autorizado, aprovações por tarefa, tentativas, observações e readback;
- `slices/slices.md` para a prévia humana corrente.
- `slices/divergence.md` para a correção exata e o impacto apresentados antes de alinhar o pai;
- `slices/change-review.md` para classificação, impacto localizado e itens que permanecem válidos;
- `slices/revision-application.md` para a prévia concreta das mutações e preservações;
- `.flow/slices-publication.json` para revisão final, aprovação, IDs, tentativas, observações e conclusão da publicação;
- `.flow/slices-reconciliation.json` e `slices/reconciliation.md` para a decisão e a prévia exata de uma materialização local de publicação histórica;
- `.flow/slices-dependencies.json` para revisões, aprovações, operações e readbacks de dependências externas;
- `slices/publication.md` para a prévia final aprovada;
- `tasks/dev-<id>-<slug>/task.md`, `tasks/qa-<id>-<slug>/task.md` e `tasks/study-<id>-<slug>/task.md` para as representações canônicas criadas somente depois do readback integral do respectivo fluxo.

Rejeite links simbólicos em qualquer caminho gravado. Grave candidatos na mesma pasta e substitua atomicamente somente depois de validar. Preserve o estado anterior para executar a validação de transição; revisões e aprovações são append-only.

## Conferência do item pai

O helper aceita estados v2–v4 do `project-flow`, mas a entrada deve ser Feature ou Bug, estar `completed`, conter `redmine.issue_id`, uma aprovação `requirement` válida e nenhuma divergência pendente. O snapshot sanitizado é a resposta estruturada da issue, limitada aos campos públicos necessários pelo verificador (`id`/`issue_id`, `subject`, `description` e, quando presentes, `status`, `status_id` e `relations`). Ele não contém cabeçalhos, credenciais ou configuração do MCP. Exemplo abreviado:

```json
{
  "issue": {
    "id": 123,
    "subject": "[WEB] [OPERACIONAL] Gestão de Usuários",
    "description": "<!-- project-flow:start -->...<!-- project-flow:end -->"
  }
}
```

Execute:

```sh
python <project-slices>/scripts/manage_slices.py check-input <feature-dir> --remote .work/slices-remote.json --output .flow/slices-input-check.json --at "<ISO-8601>"
```

O agente obtém a projeção remota; o script faz a comparação efetiva de identidade, título e seções funcionais gerenciadas e não chama a API. Conteúdo, atribuição ou delimitadores divergentes bloqueiam a proposta. O validador estrutural não prova legibilidade ou qualidade semântica dos cortes; aplique a disciplina e seus cenários de avaliação antes da aprovação.

Quando existir `.flow/slices-divergence.json`, `check-input`, aprovação e publicação das filhas permanecem bloqueados até o estado `completed`, com correção local atual e readback remoto verificado. Estados `pending`, `rejected`, `approved`, `local-aligned` e `aligning` são retomáveis, mas não autorizam filhas.

## Proposta e aprovação

Crie `.work/slices-proposal.json` conforme `schemas/slices-state.schema.json` e os exemplos de campo em `templates/slices.md`. O objeto da proposta possui `feature`, `inspection`, `requirements`, `slices`, `coverage` e `decisions`. Registre e renderize:

```sh
python <project-slices>/scripts/manage_slices.py record-proposal .flow/slices-state.json .work/slices-proposal.json --input-check .flow/slices-input-check.json --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo da revisão>"
python <project-slices>/scripts/manage_slices.py render .flow/slices-state.json slices/slices.md
```

Cada execução de `record-proposal` acrescenta uma revisão imutável e invalida a aprovação corrente. Depois da confirmação explícita do tech lead, preserve uma cópia do estado anterior e execute:

```sh
python <project-slices>/scripts/manage_slices.py approve .flow/slices-state.json --actor "<tech lead>" --at "<ISO-8601>"
python <project-slices>/scripts/manage_slices.py validate .flow/slices-state.json --previous <estado-anterior.json>
```

`approve` relê o requisito e o estado aprovados e confere título, identidade e caminhos contra o `input-check`; uma alteração desde a conferência exige novo `check-input` e nova proposta. `technical_context` pode ser omitido ou `null`; inclua texto e renderize a seção somente quando uma decisão aprovada tornar esse contexto necessário.

**Concluído quando:** a revisão aprovada, sua prévia Markdown, o hash e a atribuição sobrevivem em arquivos versionáveis fora de `.work/`, e nenhuma revisão anterior foi alterada.

Depois desta aprovação local, siga [publicação DEV e QA](publication.md). O plano e snapshots remotos continuam descartáveis em `.work/`; estado, aprovações e progresso permanecem em `.flow/`, e a prévia fica em `slices/` até a materialização canônica por ID em `tasks/`.

Quando a publicação já foi concluída por um contrato histórico v1, siga [reconciliação local](legacy-reconciliation.md) em vez de preparar ou repetir operações remotas.

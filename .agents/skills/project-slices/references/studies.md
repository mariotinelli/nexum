# Estudo excepcional e retomada

Este ramo publica uma única filha DEV excepcional quando a disciplina de `vertical-slicing` identifica uma incerteza que impede a proposta completa. Ele não publica DEV ou QA restantes e nunca conclui o fatiamento, o item pai ou o item corrente do escopo.

## Preparar e aprovar

Registre `.work/slices-study-plan.json` com a fonte `slices-input-check.json`, snapshots sanitizados do pai e dos metadados, campos nativos e `study` contendo `subject`, `question`, `expected_result`, `effort_limit` e `estimate_hours`. A descrição deve ser compreensível sem a conversa. Execute:

```sh
python <project-slices>/scripts/manage_study.py prepare .flow/slices-study.json .work/slices-study-plan.json --input-check .flow/slices-input-check.json --preview slices/study.md --actor "<tech lead>" --at "<ISO-8601>" --reason "<motivo>"
```

O helper deriva exatamente `[DEV] <título completo do item pai> - Estudo: <assunto>`, preservando todos os tokens do pai. A identidade provisória permanece somente no estado e na prévia `slices/study.md`. Mostre a prévia integral e seu hash. A aprovação é específica para esse hash e exclusivamente do tech lead:

```sh
python <project-slices>/scripts/manage_study.py approve .flow/slices-study.json --actor "<tech lead>" --at "<ISO-8601>"
```

**Concluído quando:** pergunta, resultado esperado, limite, campos nativos, descrição e hash foram apresentados, e o estado `approved` contém a aprovação tech-lead da revisão corrente.

## Publicar sem duplicar

Rode `begin-create` antes de `redmine_create_issue` e `finish-create` depois. Resultado incerto exige busca completa por `project-slices-study` em filhas abertas e fechadas e `observe-create` antes de repetir. Uma criação reconciliada conserva o mesmo `remote_id`; nova execução nunca chama o MCP novamente para esse Study.

```sh
python <project-slices>/scripts/manage_study.py begin-create .flow/slices-study.json --at "<ISO-8601>"
python <project-slices>/scripts/manage_study.py finish-create .flow/slices-study.json --attempt 1 --outcome completed --issue-id 501 --at "<ISO-8601>"
```

Depois da criação ou reconciliação, releia o pai e o Study com todos os campos e relações em `.work/slices-study-readback.json`, então execute:

```sh
python <project-slices>/scripts/manage_study.py complete .flow/slices-study.json --readback .work/slices-study-readback.json --at "<ISO-8601>"
```

O readback tem `parent` e `study`. O helper exige o conteúdo e os campos nativos aprovados, o ID reconciliado, relações completas e o status de execução original do pai. Somente então grava atomicamente o estado confirmado e `tasks/study-<id>-<slug>/task.md`; status, responsável e datas operacionais não entram no artefato. Uma pasta já existente para o mesmo tipo e ID fixa o slug e é reutilizada nas retomadas. Falha, ambiguidade, divergência ou readback incompleto preserva apenas o estado retomável e não cria uma pasta canônica.

O estado passa a `awaiting-result`, que significa fatiamento em andamento/pausado por evidência. Não prepare a publicação DEV/QA ordinária nem marque o item pai ou o escopo como concluído.

**Concluído quando:** a criação está reconciliada uma única vez, o readback integral preserva o status do pai, o ID e o slug são duráveis, o `task.md` contém apenas identidade e conteúdo estáveis e nenhuma filha futura foi antecipada.

## Registrar o resultado e retomar

Sem resultado, `resume` recusa avançar. Quando houver resultado, grave em `.work/slices-study-result.json` o `study_remote_id`, `result`, `source` (`kind` e `reference`), `authored_by` e `authored_at`; depois execute `record-result` com quem registrou e quando. O helper vincula a evidência à pergunta, limite, revisão aprovada, ID remoto e bytes da fonte.

Prepare `.work/slices-proposal.json` como proposta completa nova e execute:

```sh
python <project-slices>/scripts/manage_study.py resume .flow/slices-study.json .work/slices-proposal.json --slices-state .flow/slices-state.json --input-check .flow/slices-input-check.json --actor "<tech lead>" --at "<ISO-8601>" --reason "<como o resultado orientou a revisão>"
```

O helper incorpora `study_evidence`, acrescenta uma revisão imutável com a mesma base semântica do fatiamento ordinário e deixa `slices-state.json` como `proposed`. Mostre a proposta renderizada e retome a aprovação ordinária; a aprovação excepcional do Study não vale para a decomposição.

Study é evidência para o novo fatiamento, não trabalho executável pelo Ralph: sua pasta recebe somente `task.md`; `planning.md` continua exclusivo de DEV ordinária.

Na publicação ordinária posterior, a descoberta de filhas apresenta o Study novamente ao tech lead. Preserve seu ID e baseline como filha existente `keep-external`; ele não ocupa uma key DEV da decomposição e o caminho somente QA continua exigindo cobertura `existing` integral.

**Concluído quando:** o resultado atribuído e fonte permanecem íntegros, a nova revisão os cita explicitamente e nenhuma aprovação ordinária está válida antes da nova decisão do tech lead.

# Aplicação de revisão aprovada

Use esta fase após uma revisão funcional corrente estar `authorized`. Leia primeiro a [disciplina de aplicação de revisões](../../vertical-slicing/references/revision-application.md). O helper processa somente JSON e Markdown locais; o agente executa leituras e mutações pelos tools do MCP Redmine.

## Preparar o delta

Releia pai, todas as filhas abertas e fechadas e todas as relações; grave em `.work` um snapshot sanitizado `{"parent": {...}, "tasks": [...], "relations": [...], "complete": true}`. Use os objetos de issue do MCP, com `project`, `parent`, `tracker`, `status` com ID e nome, e `journals` para comprovar cancelamentos. Marque `complete` somente após consumir todas as páginas. Consulte também os status nativos e grave `{"statuses": [{"id": 1, "name": "..."}]}`. O plano local contém `preview_snapshot`, `status_metadata`, mapeamento explícito de `not_started`, `in_progress`, `completed` e `cancelled`, e operações `create`, `update`, `cancel`, `relation-add` ou `relation-remove`.

Cada operação liga `revision_sha256` ao hash aprovado e lista somente `impact_ids` autorizados. Criações carregam o pai, título e descrição que cita esse hash; o payload acrescenta um marcador estável de reconciliação à descrição. Cancelamentos carregam o status nativo exato, motivo e `replacement_keys`; relações descrevem uma aresta nativa `blocks`. Execute `prepare` com `--change-review`, `--publication-state` e `--preview`. Mostre a prévia completa ao tech lead, incluindo os atributos exatos. Após sua aprovação, execute `approve --proposal-sha256 <hash retornado por prepare> --actor "<tech lead>" --at "<ISO-8601>"`. A autorização semântica identifica o impacto; esta aprovação vincula a execução à prévia concreta.

Para novas filhas, use uma `task_key` inédita. Em `relation-add`, `attributes.issue_id` e `attributes.issue_to_id` aceitam um ID publicado ou uma chave como `dev-new` e `qa`; o helper resolve a chave após confirmar a criação. Execute criações antes das relações e dos cancelamentos que dependem delas. Use chaves de operação inéditas em ciclos seguintes.

**Concluído quando:** o hash da prévia concreta foi aprovado pelo tech lead, revisão e publicação estão atuais, todo status possui ID e nome nativos, cada operação cabe no impacto aprovado e a prévia distingue tarefas novas, em andamento, concluídas e não iniciadas.

## Aprovar tarefas sensíveis

Para cada atualização em andamento e cada cancelamento, releia o snapshot completo e execute `approve-task --key ... --snapshot ... --actor ... --reason ...`. A aprovação adicional é exclusiva do tech lead e fica ligada ao hash da tarefa corrente e da intenção. Atualizações de tarefa não iniciada, criações e relações não exigem outro aprovador.

**Concluído quando:** toda tarefa em andamento ou cancelada possui aprovação específica sobre o snapshot e a mutação atuais; nenhuma aprovação ampla ou antiga foi reaproveitada.

## Aplicar e retomar

Antes de cada chamada, produza novo snapshot e execute `begin --key ... --snapshot ...`; o comando retorna o tool e payload exatos. Registre a resposta com `finish`. Resultado `unknown` ou queda após `begin` exige readback completo e `observe --outcome matched|absent` antes de repetir. A observação vale para a última tentativa: `absent` exige busca completa sem resultado correspondente; múltiplos resultados ou conteúdo alterado mantêm a reconciliação pendente. Para `matched` de criação ou adição informe o ID remoto observado.

O helper recusa snapshot alterado desde a prévia, tarefa concluída, cancelamento sem prova de não início, impacto ampliado e operação já concluída. Reconcile a mudança por uma nova execução de `prepare`. Preserve no plano as operações já concluídas da aplicação parcial e reconcilie tentativas incertas antes de replanejar. Uma intenção alterada que já teve tentativa recebe nova chave. Apresente a nova prévia e registre suas aprovações, preservando IDs, resultados e aprovações anteriores no histórico.

**Concluído quando:** toda operação está concluída uma vez, com tentativas e observações append-only e sem duplicação após falha parcial.

## Conferir e concluir

Releia pai, tarefas e relações e execute `complete --readback`. O helper exige payload/status de cada mutação, evidência legível de cancelamento, bloqueios DEV→QA afetados, preservação exata de tarefas e relações não afetadas e o mesmo status do pai.

Somente depois dessa conferência integral, `complete` substitui atomicamente o `task.md` de cada filha gerenciada cujo conteúdo ou relações pertencem ao delta autorizado. O helper reutiliza o caminho encontrado por tipo e ID, preservando o ID e o slug fixado na primeira materialização, e aplica as mesmas regras de conteúdo estável da publicação inicial. Filhas concluídas, externas, adotadas mas não afetadas e todas as filhas fora do delta conservam seus arquivos byte a byte. Falha, resultado incerto, aplicação parcial, readback divergente ou artefato local alterado mantêm o `task.md` corrente intacto.

**Concluído quando:** `.flow/slices-revision-application.json` está `completed`, o readback e as substituições canônicas estão hash-bound, somente os `task.md` do delta autorizado mudaram e os históricos anteriores de adoção/externalidade, Study, divergência e revisão semântica permanecem preservados.

Após concluir uma aplicação, uma nova mudança do requisito pode iniciar outro ciclo nos mesmos arquivos de estado. A revisão seguinte incorpora IDs de filhas e relações criadas pelos ciclos concluídos. As evidências de requisitos, prévias, observações e readbacks são copiadas para arquivos identificados pelo conteúdo; preserve esses arquivos junto aos estados.

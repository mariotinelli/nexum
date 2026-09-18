---
name: project-slices
description: Prepare, approve, publish, and safely resume vertical DEV and QA child issues for an approved project-flow Feature or scope. Use when a tech lead wants an implementation breakdown, sequential scope slicing, native Redmine children and blockers, or interrupted publication reconciliation.
---

# Project Slices

Responda em português brasileiro (pt-BR) desde o primeiro anúncio. Este fluxo é operado e aprovado exclusivamente pelo tech lead. Ele transforma Features canônicas do `project-flow` em trabalho DEV e QA publicado; preserva o estado de execução das Features e nunca atribui à QA uma decisão de aprovação.

## Escolher o ramo

Com uma Feature informada, siga diretamente o fluxo individual abaixo. Com um escopo informado, ou sem entrada, leia [fatiamento sequencial de escopo](references/scope-orchestration.md). O ramo de escopo seleciona e acompanha Features, mas chama este mesmo fluxo individual para cada uma; suas aprovações nunca são coletivas.

**Concluído quando:** a entrada foi classificada como Feature ou escopo e, sem entrada, o tech lead escolheu entre os escopos elegíveis apresentados.

## Preparar a entrada

Leia [entrada e persistência](references/input-and-persistence.md) antes de gravar qualquer artefato. Exija o diretório de uma Feature com `feature.md`, estado concluído, aprovação local válida e `redmine.issue_id`. Consulte a Feature pelo MCP Redmine, salve apenas o objeto estruturado e sanitizado da issue na área temporária e rode `check-input`. O helper reutiliza o verificador funcional do `project-flow`, inclusive para layouts que preservam os bytes aprovados e alteram somente destinos de links. Uma divergência entre requisito canônico, estado ou projeção remota interrompe a aprovação.

**Concluído quando:** a identidade da Feature, o hash aprovado, o vínculo Redmine e o alinhamento remoto foram conferidos sem divergência.

## Revisar mudança do requisito

Quando já existir publicação concluída e o requisito aprovado atual diferir da versão registrada em seu baseline semântico, leia [revisão de mudança do requisito](references/change-review.md) antes de inspecionar ou preparar qualquer nova tarefa. Diferença de bytes abre a comparação, mas somente a análise semântica distingue mudança editorial de funcional. Preserve a publicação corrente enquanto a revisão estiver pendente ou rejeitada.

**Concluído quando:** a mudança editorial está registrada sem invalidar o fatiamento, ou a mudança funcional possui classificação, impacto localizado e decisão específica do tech lead antes de qualquer preparação de mutação.

## Aplicar a revisão aprovada

Quando uma mudança funcional possuir a autorização localizada corrente, leia [aplicação de revisão aprovada](references/revision-application.md). Releia cada tarefa antes da mutação, preserve tarefas concluídas e históricos anteriores, e trate criações, atualizações, cancelamentos e relações como operações retomáveis. Tarefa em andamento e cancelamento de tarefa não iniciada exigem aprovação adicional do tech lead ligada ao snapshot e à mutação exatos.

**Concluído quando:** o readback prova todo o delta autorizado, preserva tarefas e relações fora dele e mantém o status de execução do pai.

## Inspecionar o código

Leia a Feature com `children` e siga [filhas existentes e caminho somente QA](references/existing-children.md) quando ela já possuir filhas. Toda filha descoberta precisa de uma decisão explícita do tech lead antes da proposta final.

Inspecione obrigatoriamente o repositório e as capacidades relacionadas antes de propor cortes. Registre evidências suficientes para classificar cada parte como criação, adaptação ou comportamento existente. Inclua arquivos ou símbolos somente como evidência da inspeção; contexto técnico na descrição é opcional e depende de decisão aprovada, sem virar receita de implementação.

**Concluído quando:** todo comportamento da Feature tem evidência técnica e nenhuma lacuna funcional ou divergência permanece aberta.

Se a inspeção ou os cortes propuserem comportamento ausente do requisito aprovado, leia [divergências materiais e alinhamento do pai](references/divergences.md). Mostre ao tech lead a correção exata e o impacto nas filhas. Rejeição mantém requisito e pai intactos e bloqueia as filhas; aprovação alinha primeiro o requisito canônico local e depois o pai remoto, com operação retomável e readback. API consumível ausente do requisito é sempre divergência material. Depois do alinhamento, descarte a autoridade das aprovações anteriores e refaça proposta e aprovação ordinárias sobre a fonte corrigida.

**Concluído quando:** a correção foi rejeitada e as filhas afetadas continuam bloqueadas, ou os alinhamentos local e remoto foram verificados e uma proposta nova ainda aguarda sua aprovação ordinária.

Se uma incerteza técnica impedir o fatiamento vertical completo, leia [estudo excepcional e retomada](references/studies.md). O Study é o único ramo que pode publicar uma filha antes da proposta completa e exige aprovação específica do tech lead; sua existência mantém este fluxo em andamento.

**Concluído quando:** a inspeção sustenta uma proposta completa ou delimita uma única incerteza impeditiva para o ramo de Study.

## Propor e revisar

Invoque `vertical-slicing` com o requisito aprovado e as evidências de código. Materialize a proposta conforme [entrada e persistência](references/input-and-persistence.md), valide-a com `record-proposal` e renderize `slices/slices.md`. Apresente a prévia numerada com título, entrega verificável, esforço humano com agentes, bloqueios e tabela de cobertura. Para capacidade de outra Feature, leia [dependências externas e refinamento](references/dependencies.md) antes de propor a aresta. Pergunte sobre granularidade, união, divisão, estimativas e arestas de bloqueio; registre cada nova versão sem reescrever as anteriores.

Uma única filha DEV é válida. Seis horas são referência, não limite: toda estimativa acima disso traz justificativa legível, sem divisão artificial. Uma preparação técnica excepcional precisa revelar a entrega que viabiliza. API só aparece no título quando ela própria é uma entrega consumível já aprovada na Feature.

**Concluído quando:** o tech lead confirma que granularidade, títulos, estimativas, bloqueios e cobertura da revisão corrente estão corretos.

## Aprovar a decomposição

Mostre as descrições completas renderizadas antes da aprovação. Elas devem ser humanas e conter entrega, limites, critérios verificáveis de sucesso, erro e permissão quando relevantes, dependências e rastreabilidade. Renderize contexto técnico somente quando houver conteúdo aprovado. Use uma única seção de critérios; planejamento de arquivos, código e testes automatizados pertence à implementação posterior.

Rode `approve` informando o tech lead e o instante da decisão, depois `validate --previous` contra o estado anterior. Esta decisão aprova a decomposição; a autorização para publicar depende da prévia final separada.

**Concluído quando:** a aprovação referencia exatamente o hash da revisão corrente, o estado local valida como `approved` e os caminhos dos artefatos são informados ao tech lead.

## Preparar e publicar filhas

Leia [publicação DEV e QA](references/publication.md). Confirme os metadados nativos, componha uma QA para a Feature e materialize a prévia final com descrições e campos completos. Obtenha a aprovação explícita do tech lead para o hash dessa prévia antes da primeira mutação. Publique pelo MCP Redmine existente e registre cada resultado no helper local; após resultado incerto, leia antes de repetir. Ao final, releia pai, filhas e relações e só conclua quando todos os campos e bloqueios aprovados estiverem conferidos.

**Concluído quando:** todas as filhas possuem IDs reconciliados, cada DEV necessária bloqueia nativamente a QA, o readback integral confere e o estado de execução original da Feature permanece igual.

## Configurar dependências externas

Quando a decomposição aprovada contém `external_blockers`, siga [dependências externas e refinamento](references/dependencies.md). Configure relações específicas quando as filhas fornecedoras existirem; caso contrário, use a Feature fornecedora provisoriamente com o motivo aprovado. Ao surgirem as filhas, apresente ao tech lead a substituição exata, adicione e confira os bloqueios específicos e só então remova a relação provisória controlada por este fluxo.

**Concluído quando:** toda dependência externa aprovada possui relação nativa conferida, o grafo relevante permanece acíclico e o estado distingue roteamento pronto de capacidade implementada.

## Limites

Cada execução individual trabalha uma Feature dependente por vez e gerencia somente as filhas que o tech lead adotou ou aprovou criar. O ramo de escopo somente as coordena na ordem do catálogo. Filhas mantidas fora permanecem intocadas. A fase de divergência corrige somente o pai necessário aos cortes correntes e nunca amplia escopo silenciosamente. Scripts deste pacote manipulam somente JSON e Markdown locais; todo acesso remoto acontece exclusivamente pelo MCP Redmine e sua sessão protegida.

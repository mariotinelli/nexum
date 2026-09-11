# Entrevista — Consulta de Tarefas (#1014465)

## Evidências e árvore inicial

Catálogo aprovado, design-tasks, design-guide e Gestão de Tarefa (#1014454). Relação nativa 665 confirmada; status New preservado. Fontes compartilhadas já normalizadas; leitura estática adicional de tarefas.html, funções filtered, tasksPage e tratamento de filtros, sem execução do protótipo.

Fatos das referências: busca em título, filtros combinados por E; projeto, situação, prioridade e responsável com seleção única; Prazo até inclusivo exclui tarefas sem prazo; aplicar redefine página. Ordenação por criação/atualização decrescente, prioridade Urgente→Baixa, prazo crescente com sem prazo no fim; oito registros por página. A busca demonstrada ignora caixa, mas não acentos. A origem Projeto e filtros salvos podem conflitar no protótipo; Limpar não explicita a redefinição de página. Esses pontos são evidência, não decisões de implementação.

Regras herdadas: somente tarefas não arquivadas dos projetos acessíveis, incluindo consulta dos projetos arquivados; sem acesso administrativo automático. Situações consultáveis Pendente, Em andamento, Pausada, Finalizada e Cancelada; atraso somente nas três primeiras. Nova tarefa usa a permissão de gestor de projeto ativo já aprovada. Sem ações de execução nesta consulta; detalhe e criação pertencem à Gestão de Tarefa. Sem filtro ativo, consultar todas as situações admitidas. Não reabrir decisões de autorização nem pedir mecanismos técnicos.

Fronteira Q63–Q68: busca, opções de responsável, ordenação, paginação, entrada pelo projeto e duração da preservação dos filtros. Perguntas independentes; descendentes somente se as respostas alterarem seleção, ordenação ou navegação. Não há decisão adiada ou pergunta a terceiro neste momento.

## Q63 — Correspondência da busca

A busca deve encontrar qualquer trecho do título, ignorando maiúsculas/minúsculas, acentos e espaços nas extremidades?

Recomendação: sim. Por exemplo, “revisao” encontra “Revisão do contrato”; texto vazio não restringe a consulta. Isso amplia a normalização demonstrada pelo protótipo.

Estado: blocking. Resposta: aguardando.

## Q64 — Filtro de responsável

O filtro deve oferecer Todos, Sem responsável e as pessoas dos projetos acessíveis, incluindo responsáveis inativos que ainda tenham tarefas? Ao selecionar um projeto, limitar as pessoas a esse projeto?

Recomendação: sim. Mantém a consulta de atribuições antigas e permite localizar tarefas ainda não distribuídas, sem listar pessoas de projetos sem acesso.

Estado: blocking. Resposta: aguardando.

## Q65 — Ordenação

Podemos usar Criação mais recente como padrão; Atualização mais recente; Prazo mais próximo, com tarefas sem prazo no fim; e Prioridade de Urgente para Baixa? Em empate, usar criação mais recente?

Recomendação: sim, mantendo as direções demonstradas no protótipo e tornando o desempate previsível.

Estado: blocking. Resposta: aguardando.

## Q66 — Paginação

Manter oito tarefas por página, com total encontrado e Anterior/Próxima, voltando à primeira página ao aplicar ou limpar filtros?

Recomendação: sim, seguindo a referência. Ao voltar do detalhe, preservar filtros e página; se a página não existir mais, abrir a última disponível.

Estado: blocking. Resposta: aguardando.

## Q67 — Entrada pelo projeto

Ao abrir Ver tarefas dentro de um projeto, devemos aplicar somente esse projeto e limpar os demais filtros anteriores?

Recomendação: sim, para que um filtro antigo de outro contexto não esconda tarefas do projeto escolhido. O usuário pode alterar ou limpar o filtro depois.

Estado: blocking. Resposta: aguardando.

## Q68 — Preservação dos filtros

Manter filtros e ordenação ao navegar e atualizar a página, mas reiniciar no padrão depois de sair da conta e entrar novamente?

Recomendação: sim, interpretando a persistência na sessão aprovada no catálogo como continuidade durante o acesso atual. Limpar remove busca e filtros, restaura a ordenação padrão e retorna à primeira página.

Estado: blocking. Resposta: aguardando.

## Respostas Q63–Q68 — 2026-09-10T14:49:18.391854Z

Proveniência: Mário Tinelli, resposta direta nesta conversa.

### Q63

Resposta literal: sim, inclusive trecho da descrição também

Decisão: Buscar qualquer trecho no título ou na descrição, ignorando maiúsculas/minúsculas, acentos e espaços nas extremidades. Amplia a busca apenas em título do catálogo.

### Q64

Resposta literal: concordo

Decisão: Filtro de responsável oferece Todos, Sem responsável e pessoas dos projetos acessíveis, incluindo responsáveis inativos que ainda tenham tarefas; selecionar projeto limita pessoas a esse projeto.

### Q65

Resposta literal: concordo

Decisão: Ordenação padrão criação mais recente; atualização mais recente; prazo mais próximo com sem prazo no fim; prioridade Urgente para Baixa. Desempate por criação mais recente.

### Q66

Resposta literal: pode ser

Decisão: Oito tarefas por página, total encontrado e Anterior/Próxima. Aplicar/limpar filtros retorna à primeira página; voltar do detalhe preserva filtros e página. Se a página não existir mais, abrir a última disponível.

### Q67

Resposta literal: concordo

Decisão: Entrar por Ver tarefas do projeto aplica somente esse projeto e limpa os demais filtros anteriores.

### Q68

Resposta literal: concordo

Decisão: Preservar filtros e ordenação ao navegar e atualizar; reiniciar no padrão após sair da conta e entrar novamente. Limpar remove busca/filtros, restaura ordenação padrão e primeira página.

Q63 substitui o limite de busca apenas em título. Catálogo e operações anteriores preservados; avanço pausado para revisão completa. Q64 abre o comportamento da seleção de responsável quando o projeto muda. Demais respostas resolvidas, sem escolhas técnicas.

## Q69 — Responsável após trocar o projeto

Se o responsável selecionado não fizer parte das opções do novo projeto, devemos redefinir esse filtro para Todos, mantendo os demais filtros?

Recomendação: sim, evitando uma seleção inválida e resultados vazios por um filtro que deixou de estar disponível. Se o responsável continuar válido, mantê-lo. Isso vale para a troca dentro dos filtros; a entrada por Ver tarefas do projeto já limpa os demais filtros conforme Q67.

Estado: blocking. Resposta: aguardando.

## Resposta Q69 — 2026-09-10T14:56:10.875178Z

Mário Tinelli respondeu literalmente: pode ser.

Decisão: ao trocar o projeto dentro dos filtros, redefinir responsável para Todos apenas se inválido no novo projeto; manter seleção válida e demais filtros. Q69 resolvida.

## Auditoria e síntese para confirmação

Q63–Q69 resolvidas. Consulta restrita a projetos com participação, sem tarefas arquivadas; inclui situações Pendente, Em andamento, Pausada, Finalizada e Cancelada. Projetos arquivados mantêm consulta. Busca em trechos de título ou descrição, ignorando caixa, acentos e espaços externos. Filtros combinados por E; Prazo até inclusivo exclui sem prazo; atraso respeita Gestão de Tarefa. Responsáveis conforme Q64/Q69, ordenação Q65, paginação Q66, entrada contextual Q67 e persistência Q68. Interface tabela/cards e estados de carregamento/vazio/erro/sucesso, detalhe e criação segundo permissões já aprovadas. Sem nova decisão técnica.

Nenhuma lacuna funcional conhecida, contradição de fonte sem resolução ou pergunta a terceiro. A ampliação da busca contradiz o limite antigo do catálogo e está resolvida por Q63; sua projeção completa ainda precisa de reaprovação. Aguardar confirmação explícita desta síntese antes de preparar a revisão completa e o requisito. Estados permanecem pausados pelo gate de catálogo.

## Confirmação explícita do entendimento — 2026-09-10T15:00:58.053962Z

Mário Tinelli respondeu literalmente "confirmo" à síntese completa de Consulta de Tarefas. Q63–Q69 e entendimento confirmados; nenhuma lacuna funcional conhecida. Preparar revisão integral do catálogo e requisito para aprovação, preservando o gate vigente.

## Proposta conjunta pronta — 2026-09-10T15:03:29.360716Z

Catálogo completo catalog-search-review.md, SHA-256 b94fa4965f81118c562e5c88e70b8111fc44f74b77a878f2865f2c75b0f9bc18; apenas search-tasks-01 e a operação de busca da entrega foram ampliados, preservando nomes, públicos, onze itens, ordem, sete issues, fontes, grafo e relações. Candidato separado validado contra o canônico, mantido intacto até aprovação.

feature.md completo com 13 seções e 17 critérios de aceite, SHA-256 be8196258e268563209b2f658d5b37a48992ab9f102d9f9cd4d392014e468e32. Links, estados e transição do catálogo validados. Entendimento confirmado e nenhuma lacuna funcional conhecida. Aguardar aprovação explícita conjunta; registrar primeiro o catálogo e retomar, depois aprovar o requisito em transições sequenciais. Nenhuma publicação autorizada por esta proposta.

## Aprovação conjunta — 2026-09-10T15:05:44.502887Z

Mário Tinelli respondeu "sim" ao catálogo completo revisado e ao requisito. Aprovações catalog-search-review-001 e requirement-search-001 registradas; requisito SHA-256 489fc54a956488fedb584a56047fa182e9520e4042e0bced4a3dcb6b08d32ea6. Rótulos editoriais atualizados para aprovado. Pausas resolvidas e requisito aprovado; preparar publicação separada, mantendo status New.

## Prévia de publicação — 2026-09-10T15:06:25.927117Z

Descrição completa em publication-preview.md; payload em publish-payload.json, SHA-256 9de4afd44f81127044163cfaaebf253f698af1bb289dd8965cb182d7f52c8e4f. Atualizar somente description da issue #1014465; status New preservado. Sem conteúdo humano externo ou divergências internas; relação blocks:1014454:1014465 (665) já existente. Aguardar aprovação explícita da publicação.

## Publicação e conclusão — 2026-09-10T15:09:11.823972Z

Mário Tinelli respondeu "sim" à prévia completa. Aprovação publish-search-001 registrada antes da atualização; resultado persistido e releitura confirmou descrição aprovada, status New e relação 665. Hash gerenciado 4f2d1c60ac5c5b4a8a583bcf98ae3aadf7969ff0eba03e29f7b86aacf6df2126. Estados e transições válidos; nenhuma pendência funcional. Requisito pronto para planejamento técnico.

## Revisão publicada após Gestão de Tempo

Mário Tinelli aprovou o catálogo completo, os quatro documentos e as quatro publicações em etapas explícitas. A descrição de #1014465 foi publicada e relida: status New e relações preservados, sem divergência ou conteúdo externo alterado. Registro da revisão em ../../scopes/2026-09-09-nexum-scope/requirements-time-review.json; operações remotas anteriores preservadas como histórico. Concluído em 2026-09-10T19:09:37.970937Z.

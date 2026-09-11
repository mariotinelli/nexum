# Entrevista — Minhas Tarefas

Issue: #1014547. Responsável pelas decisões: Mário Tinelli.

## Fontes e decisões herdadas

- Catálogo vigente aprovado: `catalog-time-review-001`, hash `89759a4f2b30efdc34031fcc634de9df05328bbd7704229d7205a02d43d509b0`.
- [Minhas tarefas](../../../scopes/2026-09-09-nexum-scope/sources/design-my-tasks.md) e [guia](../../../scopes/2026-09-09-nexum-scope/sources/design-guide.md), normalizados integralmente no escopo. Protótipo é evidência, não implementação.
- Gestão de Tarefa #1014454 e Gestão de Tempo #1014493 aprovadas: responsabilidade pessoal, situações vigentes, pausa que salva e encerra a execução, novo início com limite próprio de oito horas, finalização integrada e proibição de controle manual do cronômetro alheio.
- Administradores também veem somente tarefas próprias nesta capacidade. O filtro de responsável demonstrado no protótipo não amplia esse recorte. As referências antigas a Bloqueada, Concluída, Retomar, Reabrir e Descartar foram substituídas pelas decisões aprovadas no catálogo e nos requisitos anteriores.
- Consulta de Tarefas #1014465 fornece precedente para busca e filtros; seus detalhes específicos não são presumidos como decisão de Minhas Tarefas.
- Aprovação explícita da criação registrada em `create-my-tasks-001`; resposta `sim` à prévia da relação registrada em `relation-time-my-tasks-001`. Relação nativa 667 criada e relida: #1014493 bloqueia #1014547. Ambas as issues permanecem New.

## Árvore de decisões

Objetivo e público resolvidos pelo catálogo. Fronteira inicial: universo de tarefas (Q96), janela de finalizadas (Q97), busca/filtros (Q98), ordenação (Q99), paginação (Q100), continuidade da consulta (Q101) e entrada para cadastro existente (Q102).

Descendentes: precedência e exclusividade dos grupos após Q96/Q97; combinação de filtro de situação com grupos; composição de opções de projeto conforme universo; retorno após ação e página esvaziada conforme Q100/Q101. Dados essenciais dos cards, responsividade, vazios e retorno de falhas têm evidência explícita; auditar sua coerência após as respostas. Permissões e regras centrais do cronômetro são herdadas, sem nova decisão técnica.

## Rodada 1 — aguardando respostas

### Q96 — Tarefas de somente consulta

**Pergunta:** Tarefas canceladas, arquivadas ou de projetos arquivados devem aparecer em Minhas Tarefas?

**Recomendação:** Excluir canceladas, arquivadas e todas as tarefas de projetos arquivados desta visão de trabalho diário; manter a consulta histórica pelos locais já previstos.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q97 — Finalizadas recentemente

**Pergunta:** Qual período define Finalizadas recentemente?

**Recomendação:** Hoje e os seis dias anteriores, pela data de finalização no horário de Brasília, para dar visibilidade à última semana de trabalho.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q98 — Busca e filtros

**Pergunta:** Podemos usar a mesma busca e os mesmos critérios de filtros da Consulta de Tarefas, mantendo o responsável fixo no usuário conectado?

**Recomendação:** Buscar trecho em título ou descrição, ignorando caixa, acentos e espaços nas extremidades; combinar projeto, situação, prioridade, Prazo até inclusivo e Apenas atrasadas por E. Prazo até exclui tarefas sem prazo; Aplicar filtros efetiva a consulta. As situações oferecidas respeitarão o universo definido em Q96.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q99 — Ordenação dentro dos grupos

**Pergunta:** Qual deve ser a ordenação padrão e quais alternativas ficam disponíveis dentro de cada grupo?

**Recomendação:** Criação mais recente como padrão; alternativas de atualização mais recente, prazo crescente com sem prazo no fim e prioridade Urgente→Baixa. Empates pela criação mais recente, seguindo a Consulta de Tarefas. A ordenação não muda a sequência dos grupos.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q100 — Paginação dos grupos

**Pergunta:** Como percorrer grupos com muitas tarefas?

**Recomendação:** Oito tarefas por página em cada grupo, com Anterior/Próxima independentes e contador do total filtrado do grupo. Isso mantém todos os grupos acessíveis e segue o tamanho de página das demais consultas. O protótipo mostra todos os cards; o guia exige paginação nas listagens.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q101 — Preservação da consulta

**Pergunta:** Ao abrir um detalhe, navegar e recarregar, devemos preservar filtros, ordenação e páginas de Minhas Tarefas até sair da conta?

**Recomendação:** Sim, com contexto próprio separado da Consulta de Tarefas. Limpar restaura o padrão; sair e entrar novamente também. Aplicar filtros reinicia a paginação.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q102 — Nova tarefa

**Pergunta:** Mantemos o botão Nova tarefa mostrado no protótipo, abrindo o cadastro já definido em Gestão de Tarefa?

**Recomendação:** Sim, somente para quem já tem permissão de criação, sem atribuição automática nem novas permissões por estar em Minhas Tarefas.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

## Confirmação do entendimento

Pendente: a rodada inicial ainda não foi respondida; requisito não aprovado nem publicado.

## Respostas da rodada 1 — 2026-09-10T19:38:07.236099Z

Proveniência: Mário Tinelli, mensagem desta conversa. As perguntas anteriores são preservadas como histórico.

### Resposta Q96

**Resposta literal:** concordo

**Entendimento:** Excluir tarefas canceladas, arquivadas e de projetos arquivados da visão de trabalho diário.

**Estado:** resolved.

### Resposta Q97

**Resposta literal:** hoje e 2 dias uteis anteriores

**Entendimento:** Finalizadas recentemente abrange hoje e os dois dias úteis anteriores. Definição de dia útil e inclusão dos dias intermediários ainda serão esclarecidas em Q103.

**Estado:** blocking para os detalhes de calendário; duração confirmada e preservada.

### Resposta Q98

**Resposta literal:** concordo

**Entendimento:** Busca e filtros conforme recomendação Q98; responsável fixo no usuário conectado.

**Estado:** resolved.

### Resposta Q99

**Resposta literal:** concordo

**Entendimento:** Ordenação conforme recomendação Q99, dentro de cada grupo.

**Estado:** resolved.

### Resposta Q100

**Resposta literal:** concordo

**Entendimento:** Oito tarefas por página em cada grupo, controles independentes e contador do total filtrado do grupo.

**Estado:** resolved.

### Resposta Q101

**Resposta literal:** concordo

**Entendimento:** Preservar filtros, ordenação e páginas até sair da conta, com contexto próprio; Limpar restaura padrão e Aplicar filtros reinicia páginas.

**Estado:** resolved.

### Resposta Q102

**Resposta literal:** sim

**Entendimento:** Manter Nova tarefa conforme recomendação Q102, com permissões existentes e sem atribuição automática.

**Estado:** resolved.

Q97 substitui a recomendação de sete dias pela duração explicitamente escolhida. Q96/Q98–Q102 não alteram o catálogo: definem detalhes da capacidade pessoal aprovada. Não há autorização de publicação nesta rodada.

## Rodada 2 — aguardando respostas

### Q103 — Dias úteis e intervalo

**Pergunta:** Como devemos tratar fins de semana e feriados no período das finalizadas?

**Recomendação:** Considerar segunda a sexta como dias úteis, sem calendário de feriados, e mostrar o intervalo inteiro entre o segundo dia útil anterior e hoje, inclusive. Na segunda-feira, incluir de quinta-feira até segunda, incluindo eventuais finalizações no fim de semana. Assim, o recuo é de dois dias úteis sem esconder trabalho realizado nos dias intermediários. Usar datas de Brasília.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q104 — Prioridade dos grupos

**Pergunta:** Uma tarefa em execução e atrasada deve aparecer somente em Em execução, mantendo o aviso de atraso?

**Recomendação:** Sim. Cada tarefa aparece uma única vez: Em execução tem precedência; Pendentes e Pausadas entram em Atrasadas, Para hoje, Próximas ou Sem prazo conforme a data; Finalizadas entram apenas em Finalizadas recentemente quando atendem ao período escolhido. Próximas inclui qualquer prazo futuro. Manter essa ordem dos seis grupos, inclusive os vazios, conforme a estrutura do protótipo e as situações vigentes.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q105 — Lista após uma ação

**Pergunta:** Após Iniciar, Pausar ou Finalizar, devemos atualizar os grupos sem sair de Minhas Tarefas, preservando filtros e páginas?

**Recomendação:** Sim, atualizar situação, contadores e grupo imediatamente após sucesso. A tarefa pode mudar de grupo ou desaparecer por não corresponder aos filtros. Se uma página deixar de existir, usar a última disponível daquele grupo; os demais preservam suas páginas. Em falha, mostrar erro e permitir nova tentativa sem indicar sucesso nem duplicar a operação. O cronômetro global continua visível mesmo quando a tarefa não corresponde aos filtros.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

## Auditoria após a rodada 1

Universo pessoal, exclusões, busca, ordenação, paginação, preservação e acesso ao cadastro estão definidos. Detalhes de calendário permanecem abertos (Q103); agrupamento depende das situações e datas já estabelecidas, não da escolha específica de feriados (Q104); retorno de ações depende da paginação já aprovada (Q105). Dados dos cards são os demonstrados: título com acesso ao detalhe, projeto, situação, prioridade, prazo ou Sem prazo, atraso e ações permitidas. Filtros de projeto respeitam acesso e projetos ativos; não há filtro para atribuição alheia. Após responder a esta fronteira, auditar integralmente e apresentar entendimento para confirmação explícita antes do documento canônico.

## Respostas da rodada 2 — 2026-09-10T19:41:04.792156Z

Proveniência: Mário Tinelli, mensagem desta conversa.

### Resposta Q103

**Resposta literal:** mudei de ideia, pegue hoje e os ultimos 6 dias, sejam ferias ou nao, dias uteis ou nao

**Entendimento:** Substituir Q97: Finalizadas recentemente inclui hoje e os seis dias corridos anteriores, inclusive fins de semana, feriados e férias, pela data de finalização em Brasília. Intervalo inclusivo, sem calendário de dias úteis.

**Estado:** resolved.

### Resposta Q104

**Resposta literal:** sim

**Entendimento:** Adotar a recomendação de Q104: grupos exclusivos, execução prevalece sobre atraso sem ocultar seu aviso; Pendentes e Pausadas por prazo; Finalizadas somente no período; seis grupos fixos inclusive vazios.

**Estado:** resolved.

### Resposta Q105

**Resposta literal:** sim

**Entendimento:** Adotar a recomendação de Q105: atualizar grupos, situação e contadores após sucesso, preservando filtros e páginas; última página disponível do grupo se a anterior desaparecer; cronômetro global visível mesmo quando a tarefa não corresponde aos filtros.

**Estado:** resolved.

Q97 foi explicitamente substituída por Q103. Preservar a decisão antiga como histórico reaberto e usar q103 como resolução vigente; não há pendência de calendário.

## Auditoria final da entrevista

Atores e permissões: catálogo e Gestão de Tarefa/Tempo; universo e exclusões: Q96; calendário: Q103; busca e filtros: Q98; ordenação: Q99; paginação: Q100; continuidade: Q101; criação existente: Q102; grupos e vazios: Q104; resultado, falhas e atualização: Q105. Dados dos cards e responsividade seguem evidência explícita. As ações e suas falhas de autorização/transição/cronômetro concorrente seguem os requisitos aprovados, sem criar novas transições. Nenhuma lacuna funcional, contradição de fonte ou pergunta adiada permanece aberta. Confirmação explícita do entendimento consolidado ainda pendente; não propor nem publicar o requisito antes desse gate.

## Entendimento consolidado apresentado para confirmação

- Mostrar somente tarefas do próprio usuário, inclusive administrador. Excluir tarefas canceladas, arquivadas e de projetos arquivados.
- Seis grupos fixos, sem duplicar tarefas: Em execução, Atrasadas, Para hoje, Próximas, Sem prazo e Finalizadas recentemente. Execução prevalece sobre atraso, preservando o aviso; Pendentes e Pausadas são agrupadas pelo prazo. Manter grupos vazios.
- Finalizadas recentemente: hoje e os seis dias corridos anteriores, pela data de finalização em Brasília, incluindo fins de semana, feriados e férias. Esta decisão substitui os dois dias úteis de Q97.
- Buscar em título ou descrição, ignorando caixa, acentos e espaços nas extremidades. Combinar projeto, situação, prioridade, Prazo até inclusivo e Apenas atrasadas; responsável fixo no usuário. Prazo até exclui tarefas sem prazo. Aplicar filtros efetiva a consulta.
- Ordenar dentro dos grupos por criação mais recente como padrão; oferecer atualização mais recente, prazo crescente com sem prazo no fim e prioridade Urgente→Baixa. Empates pela criação mais recente.
- Oito tarefas por página em cada grupo, com controles independentes e total filtrado. Preservar filtros, ordenação e páginas ao navegar e recarregar até sair da conta; contexto separado da Consulta de Tarefas. Limpar restaura o padrão e Aplicar filtros reinicia as páginas.
- Iniciar, Pausar e Finalizar seguem Gestão de Tarefa/Tempo. Pausar salva e encerra a execução; outro início abre nova execução. Após sucesso, atualizar grupos e contadores sem sair da tela, respeitando filtros. Página inexistente passa à última disponível do grupo. Cronômetro global permanece visível mesmo quando sua tarefa está filtrada; falhas permitem nova tentativa sem falso sucesso ou duplicação.
- Cards apresentam título com acesso ao detalhe, projeto, situação, prioridade, prazo ou Sem prazo, atraso e ações permitidas. Nova tarefa abre o cadastro existente para quem tem permissão, sem atribuição automática. Manter experiência responsiva e os estados de carregamento, vazio, erro e sucesso previstos no guia.

**Confirmação explícita de Mário Tinelli:** aguardando resposta à apresentação consolidada. A publicação final permanece sem aprovação.

## Confirmação explícita — 2026-09-10T19:48:45.086514Z

Mário Tinelli respondeu **sim** ao entendimento consolidado acima. Decisão understanding-my-tasks-001 registrada. Entrevista concluída sem lacunas funcionais; preparar o documento completo para aprovação. Q103 substitui Q97. A aprovação de requisito e a publicação ainda não foram concedidas.

## Documento completo preparado — 2026-09-10T19:51:31.051155Z

feature.md contém todas as seções do contrato, dez histórias, dez regras e 22 critérios de aceite. Revisão de rastreabilidade cobre as decisões confirmadas; estados do requisito e escopo válidos. SHA-256 do documento apresentado: `6c7a93bbce7ff7013f98ad93977616a8f24336b792e1c4e808fae92be56f65c6`. Aprovação do requisito pendente; nenhuma publicação executada.

## Requisito aprovado e publicação proposta — 2026-09-10T19:54:11.141397Z

Mário Tinelli respondeu **sim** à aprovação do documento completo; requirement-my-tasks-001 cobre o SHA-256 `6c7a93bbce7ff7013f98ad93977616a8f24336b792e1c4e808fae92be56f65c6`. Prévia integral em publish-preview.md e argumentos exatos em publish-payload.json; hash `9080057041ee5a9de9773e6cc750c05ee49077647d98bbf4d48d82d32985356d`. Releitura confirmou descrição inicial sem divergências, zero bytes externos aos delimitadores, status New e relação 667. Proposta altera somente a descrição; publicação aguarda aprovação explícita.

## Publicação concluída — 2026-09-10T19:56:31.422440Z

Mário Tinelli aprovou explicitamente a prévia integral, aprovação publish-my-tasks-001. Descrição publicada e relida: conteúdo corresponde ao aprovado, status New e relação 667 preservados. Operação e reconciliação concluídas; requisito válido em completed. Nenhuma lacuna funcional pendente.

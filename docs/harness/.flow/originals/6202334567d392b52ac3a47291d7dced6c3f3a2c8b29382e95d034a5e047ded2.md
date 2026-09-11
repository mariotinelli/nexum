# Entrevista — Quadro do Projeto

Issue: #1014548. Responsável pelas decisões: Mário Tinelli.

## Fontes e decisões herdadas

- [Quadro do projeto](../../scopes/2026-09-09-nexum-scope/sources/design-board.md) e [guia](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md), normalizados no escopo. Fonte do quadro lida integralmente; guia e regras aprovadas de Tarefa/Tempo já examinados neste fluxo.
- Catálogo `catalog-time-review-001`, hash `89759a4f2b30efdc34031fcc634de9df05328bbd7704229d7205a02d43d509b0`, define cinco colunas: Pendente, Em andamento, Pausada, Finalizada e Cancelada. Arquivadas ficam fora; projeto arquivado é somente consulta. Não aplicar ao quadro o recorte pessoal nem a janela de finalizadas de Minhas Tarefas.
- Administradores consultam qualquer projeto sem participação; demais usuários seguem participação vigente. Somente responsável atual executa Iniciar/Pausar/Finalizar. Cancelar/Arquivar seguem permissão de gestor do projeto ou administrador e a tabela de situações aprovada.
- Gestão de Tarefa: Pendente permite Iniciar/Finalizar/Cancelar/Arquivar; Em andamento permite Pausar/Finalizar; Pausada permite Iniciar/Finalizar/Cancelar/Arquivar; Finalizada não permite ação de situação; Cancelada permite Arquivar. Arquivar exige confirmação; nenhuma permissão permite ação fora da tabela.
- Gestão de Tempo: uma contagem por pessoa; Pausar salva e encerra a execução; novo início abre execução com limite próprio de oito horas; Finalizar salva o restante sem duplicação. Totais representam apontamentos salvos, não contagem ainda em andamento.
- A referência antiga de quatro colunas, Bloqueada/Concluída e seletor de situação foi substituída pelo catálogo e requisitos aprovados. Não oferecer arraste que altere situação, Retomar, Reabrir, Devolver à fila, Bloquear ou Descartar.
- Criação aprovada em create-board-001; relação aprovada em relation-time-board-001. Relação nativa 668 criada e relida: #1014493 bloqueia #1014548, ambas New.

## Árvore de decisões

Objetivo, público, universo por projeto, estados, permissões, dados de cards, cronômetro e somente consulta estão resolvidos por catálogo/evidências/requisitos anteriores. Fronteira inicial: ordem dos cards (Q106), paginação por coluna (Q107), entrada de cadastro contextual (Q108), preservação da navegação (Q109) e atualização após ações (Q110). Filtragem e janela de finalização de Minhas Tarefas não são transferidas a esta entrega. Ausência de filtros no quadro é coerente com a fonte e com a consulta transversal entregue separadamente.

## Rodada 1 — aguardando respostas

### Q106 — Ordem dos cards

**Pergunta:** Como ordenar os cards dentro de cada coluna?

**Recomendação:** Criação mais recente primeiro, como padrão fixo do quadro, para manter consistência com as consultas sem acrescentar novos controles de ordenação ao protótipo.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q107 — Paginação das colunas

**Pergunta:** Podemos usar oito tarefas por página em cada coluna, com navegação independente?

**Recomendação:** Sim, com Anterior/Próxima e contador do total da coluna, não somente da página. Segue o tamanho de página já aprovado e a exigência de paginação do guia. Manter as cinco colunas, inclusive vazias.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q108 — Nova tarefa no projeto

**Pergunta:** Ao acionar Nova tarefa pelo quadro, o cadastro deve abrir com o projeto atual preenchido?

**Recomendação:** Sim, respeitando as opções e permissões do cadastro existente, sem fixar o projeto além das regras já aprovadas nem atribuir automaticamente o responsável. Oferecer o botão somente a quem pode criar naquele projeto ativo.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q109 — Retorno e recarga

**Pergunta:** Ao voltar do detalhe ou recarregar, devemos preservar as páginas das colunas separadamente para cada projeto até sair da conta?

**Recomendação:** Sim. Projeto sem contexto começa na primeira página de cada coluna. Sair e entrar novamente restaura o padrão; navegar em um projeto não sobrescreve o contexto de outro.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q110 — Resultado das ações

**Pergunta:** Após uma ação no card, devemos atualizar o quadro no lugar, preservando as páginas válidas?

**Recomendação:** Sim. Atualizar situação, horas salvas e contadores; mover o card à coluna correspondente ou retirá-lo após Arquivar. Se uma página deixar de existir, usar a última disponível daquela coluna. Não forçar a abertura da página de destino do card; manter as demais páginas. Falha permite nova tentativa sem falso sucesso ou duplicação. Arquivar continua exigindo a confirmação já aprovada.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

## Confirmação do entendimento

Pendente: aguardar respostas e auditoria funcional antes de apresentar o entendimento consolidado. Requisito ainda não aprovado nem publicado.

## Respostas da rodada 1 — 2026-09-10T20:06:46.900055Z

Proveniência: Mário Tinelli, mensagem desta conversa. Perguntas anteriores preservadas como histórico.

### Resposta Q106

**Resposta literal:** concordo

**Entendimento:** Criação mais recente primeiro dentro de cada coluna, ordem fixa sem controle de ordenação.

**Estado:** resolved.

### Resposta Q107

**Resposta literal:** concordo

**Entendimento:** Oito tarefas por página de cada coluna, Anterior/Próxima independentes e contador do total da coluna; manter cinco colunas inclusive vazias.

**Estado:** resolved.

### Resposta Q108

**Resposta literal:** concordo

**Entendimento:** Nova tarefa abre cadastro com projeto atual preenchido, preservando opções e permissões existentes, sem atribuição automática; botão somente para quem pode criar nesse projeto ativo.

**Estado:** resolved.

### Resposta Q109

**Resposta literal:** concordo

**Entendimento:** Preservar páginas das colunas por projeto no retorno do detalhe e recarga até sair da conta; projeto sem contexto começa nas primeiras páginas.

**Estado:** resolved.

### Resposta Q110

**Resposta literal:** concordo

**Entendimento:** Atualizar quadro no lugar após sucesso: situação, horas salvas e contadores; mover card ou remover após Arquivar, preservando páginas válidas; última disponível da coluna quando necessário, sem forçar navegação ao card movido. Arquivar exige confirmação.

**Estado:** resolved.

## Auditoria funcional

Todas as questões da fronteira foram respondidas. Público, acesso, cinco situações, ações, campos dos cards, somente consulta em projeto arquivado e exclusão de tarefas arquivadas vêm do catálogo e dos requisitos aprovados de Tarefa/Tempo. Ordem, paginação, cadastro contextual, continuidade e resultado das ações foram resolvidos em Q106–Q110. Vazio, carregamento, erro, recuperação, responsividade e acessibilidade seguem as evidências explícitas; permissões são revalidadas, inclusive após mudança de situação ou vínculo. Horas realizadas são apontamentos salvos; execução global e bloqueio de segundo cronômetro seguem Gestão de Tempo. Não há filtro, janela de finalizadas ou recorte pessoal nesta entrega. Nenhuma lacuna funcional ou contradição permanece; aguardar confirmação explícita do entendimento consolidado antes de preparar o requisito.

## Entendimento consolidado apresentado

- Quadro de um projeto acessível a seus participantes e a administradores mesmo sem participação. Projeto arquivado mantém somente consulta.
- Cinco colunas fixas: Pendente, Em andamento, Pausada, Finalizada e Cancelada, incluindo vazias. Tarefas arquivadas ficam fora; finalizadas não têm limite de período.
- Cards mostram título com acesso ao detalhe, responsável, prioridade, prazo/atraso, estimativa e horas realizadas salvas.
- Ordem fixa por criação mais recente dentro de cada coluna; oito tarefas por página, navegação independente e contador do total da coluna.
- Preservar páginas por projeto no retorno do detalhe e recarga até sair da conta. Sem contexto anterior, começar nas primeiras páginas.
- Nova tarefa abre o cadastro existente com projeto atual preenchido, mantendo opções e permissões e sem atribuição automática. Somente quem pode criar no projeto ativo recebe o botão.
- Ações seguem Gestão de Tarefa/Tempo: Iniciar/Pausar/Finalizar exclusivos do responsável; Cancelar/Arquivar para gestores do projeto e administradores nas situações permitidas. Arquivar exige confirmação; Finalizada não permite ações de situação. Não há seletor de situação nem arraste que a altere.
- Após sucesso, atualizar situação, horas salvas e contadores no lugar; mover ou remover o card, preservar páginas válidas e ajustar somente a coluna cuja página deixou de existir. Não forçar navegação à página do card movido. Falhas não anunciam sucesso nem duplicam operações.
- Colunas empilhadas no mobile, rótulos sem depender só de cor e estados de carregamento, vazio, erro e sucesso. Cronômetro segue integralmente as regras já aprovadas de Gestão de Tempo.

**Confirmação explícita de Mário Tinelli:** pendente. Documento canônico e publicação ainda não aprovados.

## Confirmação explícita — 2026-09-10T20:07:37.935404Z

Mário Tinelli respondeu **sim** ao entendimento consolidado acima; decisão understanding-board-001. Entrevista concluída sem lacunas funcionais. Preparar documento completo para aprovação; publicação permanece sem autorização.

## Documento completo preparado — 2026-09-10T20:10:22.988409Z

feature.md apresenta todas as seções do contrato, dez histórias, dez regras e vinte critérios de aceite. Revisão de rastreabilidade cobre Q106–Q110, catálogo e capacidades herdadas; estados do requisito e escopo válidos. SHA-256 do documento apresentado: `07070b18faa7c6f9e57d543ef052f13a2b192e2458220451831a7521ad89f884`. Aprovação do requisito pendente; nenhuma publicação executada.

## Requisito aprovado e publicação proposta — 2026-09-10T20:11:49.370760Z

Mário Tinelli respondeu **sim** à aprovação do documento completo; requirement-board-001 cobre o SHA-256 `07070b18faa7c6f9e57d543ef052f13a2b192e2458220451831a7521ad89f884`. Prévia integral em publish-preview.md; argumentos exatos em publish-payload.json, hash `65ea32b987c95baf9dac32a16106cfcb3f8a9a0a3fe54609e9969ddf38d339f7`. Releitura confirmou descrição inicial sem divergências, zero bytes externos aos delimitadores, status New e relação 668. Proposta altera somente a descrição; publicação aguarda aprovação explícita.

## Publicação concluída — 2026-09-10T20:17:09.403941Z

Mário Tinelli aprovou a prévia integral, aprovação publish-board-001. Descrição publicada e relida: conteúdo aprovado, status New e relação 668 preservados. Operação e reconciliação concluídas; requisito válido em completed e sem lacunas funcionais.

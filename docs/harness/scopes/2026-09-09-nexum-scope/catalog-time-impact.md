# Revisão do catálogo — Gestão de Tempo e acesso administrativo

Prévia para aprovação, baseada nas decisões Q70–Q95 e na confirmação explícita do entendimento por Mário Tinelli. O catálogo ativo, os requisitos anteriores e suas projeções no Redmine permanecem na versão anterior até as respectivas aprovações e reconciliações.

A [projeção completa do catálogo](catalog-time-review.md) contém todos os itens ativos e retirados, entregas, cobertura, fontes, dependências, justificativas e ordem. Estado candidato: [scope-state.time-review.json](scope-state.time-review.json). Referência anterior: [scope-state.time-before.json](scope-state.time-before.json).

## Impactos

- **Nomes e classificação:** os 11 itens continuam Features, com os mesmos nomes e títulos.
- **Públicos e convenção:** WEB/PUBLICO/ADMIN/OPERACIONAL preservados. A regra compartilhada passa a reconhecer administração de qualquer projeto sem participação, mantendo os limites por responsável, cronômetro próprio e estados de somente consulta. Isso não adiciona automaticamente o administrador como participante.
- **Entregas:** acesso administrativo ampliado em projetos, tarefas, consultas, quadro e painel; apontamentos manuais/correções exclusivos de gestores e administradores; pausa gera registro e encerra execução; nova execução tem novo limite de oito horas; remoção de Descartar e ajuste das integrações.
- **Recorte pessoal:** Minhas Tarefas permanece pessoal inclusive para administradores, consumindo o novo comportamento de pausa e retomada. Perfil e autenticação mantêm seus fluxos comuns.
- **Cobertura:** 22 descrições comportamentais reconciliadas com as respostas; todos os identificadores, responsáveis e consumidores preservados. Os comportamentos restantes e exclusões continuam no catálogo.
- **Candidatos e fontes:** mesmos candidatos e mapeamentos; todas as 17 fontes e sua alocação são preservadas, sem cópia ou movimentação de evidências. As decisões da entrevista substituem apenas os trechos contraditos.
- **Dependências e ordem:** mesmos dez bloqueios ativos, mesmas posições e grupos de disponibilidade; nenhuma relação nova. As nove relações legadas retiradas são preservadas no histórico.
- **Issues:** preservadas #1014446, #1014447, #1014448, #1014449, #1014450, #1014454, #1014465 e #1014493, seus estados e relações existentes.
- **Requisitos anteriores:** preparar correções de Gestão de Projeto (#1014450), Gestão de Tarefa (#1014454) e Consulta de Tarefas (#1014465) para refletir o acesso administrativo e os ajustes de integração. Seus documentos finais e publicações exigem prévias próprias; esta aprovação de catálogo não publica nem altera essas issues automaticamente.
- **Artefatos e aprovação:** manter caminhos e histórico. A nova convenção compartilhada exige reconciliar os metadados de todos os requisitos existentes; os quatro primeiros mantêm comportamento e conteúdo. O candidato invalida a aprovação anterior apenas na prévia e ainda não contém nova aprovação nem registro de mudança aprovado. Aplicar a transição somente após a aprovação do catálogo completo.

## Catálogo completo em ordem

| Ordem | Feature | Issue | Impacto |
| --- | --- | --- | --- |
| 1 | [WEB] [PUBLICO] Autenticação | #1014446 | Fluxo preservado. |
| 2 | [WEB] [PUBLICO] Recuperação de Senha | #1014447 | Fluxo preservado. |
| 3 | [WEB] [OPERACIONAL] Meu Perfil | #1014448 | Fluxo pessoal preservado. |
| 4 | [WEB] [ADMIN] Gestão de Usuário | #1014449 | Fluxo preservado; pausa por inativação integrada por Gestão de Tempo. |
| 5 | [WEB] [OPERACIONAL] Gestão de Projeto | #1014450 | Corrigir acesso e administração sem participação; bloqueio de arquivamento por cronômetro rodando. |
| 6 | [WEB] [OPERACIONAL] Gestão de Tarefa | #1014454 | Corrigir administração sem participação; manter ações do responsável e integrar pausas/finalização. |
| 7 | [WEB] [OPERACIONAL] Consulta de Tarefas | #1014465 | Administrador consulta tarefas de qualquer projeto; demais filtros preservados. |
| 8 | [WEB] [OPERACIONAL] Gestão de Tempo | #1014493 | Consolidar as decisões de permissões, apontamentos, cronômetro, limite, consulta e totais. |
| 9 | [WEB] [OPERACIONAL] Minhas Tarefas | Ainda não criada | Preservar recorte pessoal e consumir pausa que salva/libera outra tarefa. |
| 10 | [WEB] [OPERACIONAL] Quadro do Projeto | Ainda não criada | Acesso administrativo amplo, respeitando ações do responsável e novos totais. |
| 11 | [WEB] [OPERACIONAL] Painel Gerencial | Ainda não criada | Administrador consulta equipes e indicadores de todos os projetos. |

## Alterações de cobertura

### manage-project-01

Anterior: Consultar somente projetos de que participa, filtrar ativos/arquivados, paginar e abrir dados e participantes.

Proposto: Consultar projetos de que participa; administradores consultam qualquer projeto sem participação. Filtrar ativos/arquivados, paginar e abrir dados e participantes.

### manage-project-04

Anterior: Editar dados, gestor e participantes com papéis por projeto; troca do principal preserva o anterior como Gestor salvo alteração explícita. Permitir saída ou rebaixamento do próprio gestor com confirmação e outro principal ativo.

Proposto: Gestores do projeto e administradores editam dados, gestor e participantes. Troca do principal preserva o anterior como Gestor salvo alteração explícita. Permitir saída ou rebaixamento do próprio gestor com confirmação e outro principal ativo. Administrador não precisa participar para administrar.

### manage-project-05

Anterior: Arquivar com confirmação, manter somente consulta e reativar; a Gestão de Tempo acrescenta o impedimento quando houver cronômetro aberto.

Proposto: Gestores do projeto e administradores podem arquivar com confirmação e reativar, respeitando somente consulta enquanto arquivado. Gestão de Tempo impede arquivar enquanto houver cronômetro rodando; tarefa pausada já salvou seu tempo e não mantém execução aberta.

### manage-project-09

Anterior: Respeitar autorização de gestor, confirmações, foco, estados vazios e formulários responsivos.

Proposto: Respeitar autorização de gestor do projeto ou administrador, confirmações, foco, estados vazios e formulários responsivos.

### manage-task-01

Anterior: Somente gestores do projeto criam tarefas e editam seus dados. Qualquer participante ativo pode atribuir a qualquer participante ativo, inclusive a si, ou deixar sem responsável, respeitando as situações de somente consulta.

Proposto: Gestores do projeto e administradores criam tarefas e editam seus dados. Participantes ativos e administradores podem atribuir a qualquer participante ativo, inclusive a si quando participante, ou deixar sem responsável, respeitando as situações de somente consulta.

### manage-task-03

Anterior: Restringir criação a projeto ativo gerenciado e consultas à participação. Somente o responsável atual pode Iniciar, Pausar e Finalizar; gestor apenas quando também responsável; somente gestores Cancelar, Arquivar e Desarquivar, quando permitidos. Preservar responsável inativo existente, sem novas atribuições a inativos.

Proposto: Restringir criação a projeto ativo gerenciado ou administrado; consultas dependem de participação ou acesso administrativo. Somente o responsável atual pode Iniciar, Pausar e Finalizar, inclusive quando gestor ou administrador. Gestores do projeto e administradores podem Cancelar, Arquivar e Desarquivar quando permitido. Preservar responsável inativo existente, sem novas atribuições a inativos.

### manage-task-05

Anterior: Consultar detalhe, autor, responsável, datas, estimativa e situação. Arquivar com confirmação retira das listas de trabalho, quadro e progresso. Gestores podem Desarquivar em projeto ativo, sempre para Pendente, inclusive após Cancelada → Arquivada.

Proposto: Consultar detalhe, autor, responsável, datas, estimativa e situação. Arquivar com confirmação retira das listas de trabalho, quadro e progresso. Gestores do projeto e administradores podem Desarquivar em projeto ativo, sempre para Pendente, inclusive após Cancelada → Arquivada.

### manage-task-06

Anterior: Permitir a participantes ativos comentar e anexar em tarefas finalizadas, editar/excluir somente os próprios comentários e excluir somente próprios anexos com confirmação. Descrição e comentários usam editor rico com imagens no conteúdo; anexos ficam em área separada. Sem comentários privados ou menções.

Proposto: Permitir a participantes ativos e administradores comentar e anexar em tarefas finalizadas, editar/excluir somente os próprios comentários e excluir somente próprios anexos com confirmação. Descrição e comentários usam editor rico com imagens no conteúdo; anexos ficam em área separada. Sem comentários privados ou menções.

### search-tasks-03

Anterior: Paginar somente tarefas não arquivadas dos projetos acessíveis; mostrar título, situação, responsável, prazo, prioridade, atraso e link ao detalhe.

Proposto: Paginar somente tarefas não arquivadas dos projetos acessíveis: participantes veem seus projetos e administradores podem consultar todos, inclusive arquivados para consulta. Mostrar título, situação, responsável, prazo, prioridade, atraso e link ao detalhe.

### manage-time-01

Anterior: Criar apontamento ligado a tarefa, usuário, data, duração positiva, descrição opcional e origem Manual/Cronômetro.

Proposto: Criar apontamento ligado a tarefa, pessoa, data, duração positiva, descrição opcional e origem Manual/Cronômetro. Lançamento manual exclusivo de gestores nos projetos gerenciados e administradores em qualquer projeto, para si ou outro participante atual e ativo. Data padrão hoje, passado permitido e futuro recusado. Horas decimais somente com ponto, até duas casas, maiores que zero e até 24 por registro, convertidas ao minuto mais próximo; estimativa de seis horas não limita esforço real.

### manage-time-02

Anterior: Editar/excluir somente os próprios apontamentos, com confirmação; consultar registros da tarefa e projeto acessíveis, sem aprovação de horas.

Proposto: Gestores nos projetos gerenciados e administradores em qualquer projeto podem editar/excluir apontamentos de qualquer pessoa, inclusive de origem Cronômetro. Editar tarefa, data, duração e descrição, preservando pessoa e origem; destino deve admitir o registro. Excluir exige confirmação. Participantes consultam registros dos projetos acessíveis; sem aprovação de horas.

### manage-time-03

Anterior: Filtrar por projeto, pessoa e período, paginar e somar a duração do período; apresentar modal e cards mobile.

Proposto: Filtrar Apontamentos por projeto, pessoa e período De/Até inclusivo. Inicialmente todos os projetos/pessoas acessíveis, sem limite de período; ordenar por data mais recente e desempatar pela criação mais recente. Paginar oito registros e somar todos os resultados filtrados, não somente a página; apresentar modal e cards mobile.

### manage-time-04

Anterior: Iniciar execução autorizada, pausar e voltar a iniciar, exibir tempo e tarefa globalmente e impedir outra execução aberta, incluindo pausada. Respeitar as ações e permissões da Gestão de Tarefa, sem oferecer edição direta de situação.

Proposto: Iniciar tarefa inicia seu cronômetro, exclusivo do responsável atual, inclusive para gestores e administradores; ninguém controla manualmente cronômetro alheio. Exibir tarefa e tempo globalmente e impedir mais de um cronômetro rodando por pessoa. Toda pausa salva o tempo e deixa a tarefa Pausada, liberando outra tarefa sem finalizar a anterior. Iniciar novamente começa nova execução e novo limite de oito horas.

### manage-time-05

Anterior: Finalizar criando apontamento com origem Cronômetro ou descartar com confirmação; manter contagem correta após recarregar ou fechar a página.

Proposto: Pausar automaticamente e salvar ao atingir oito horas da execução atual, sem considerar apontamentos anteriores. Finalizar salva o tempo ainda não registrado e finaliza a tarefa, sem duplicar registros; duração zero não cria apontamento. Não existe Descartar. Manter contagem após recarregar, fechar a página ou sair da conta.

### manage-time-06

Anterior: Integrar o cronômetro às ações de tarefa já entregues, respeitando o novo fluxo e suas permissões; exigir finalizar/descartar execução aberta antes de Finalizar ou Arquivar a tarefa, quando a ação for permitida, e antes de arquivar o projeto. Gestão de Tarefa funciona sem exigir cronômetro; detalhes da integração pertencem à entrevista de Gestão de Tempo.

Proposto: Integrar Iniciar/Pausar/Finalizar com tarefa e horas, respeitando responsável e transições válidas, sem exigir encerramento separado antes de Finalizar. Impedir arquivamento de projeto enquanto houver cronômetro rodando. Troca permitida de responsável, remoção de participante ou inativação da conta pausa automaticamente e salva o tempo até o instante da alteração, sem finalizar tarefa. A regra de tarefas continua pertencendo à Gestão de Tarefa.

### manage-time-07

Anterior: Atualizar horas realizadas pela soma dos apontamentos em tarefa, projeto e suas consultas; tarefas canceladas/arquivadas e projetos arquivados permitem consulta e impedem mutações.

Proposto: Atualizar horas realizadas pela soma dos apontamentos em tarefa, projeto e consultas, inclusive após correção/exclusão. Finalizadas admitem registros e correções. Tarefas canceladas/arquivadas e projetos arquivados permitem consulta e impedem mutações inclusive por administradores.

### manage-time-08

Anterior: Tratar tarefa não autorizada, duração inválida, execução já aberta, vazio e erros acessíveis; detalhes de arredondamento ficam para a entrevista.

Proposto: Arredondar cada apontamento do cronômetro para o próximo minuto inteiro; dividir execução que atravesse meia-noite por data de Brasília. Tratar tarefa não autorizada, duração inválida, outro cronômetro rodando, vazio e erros acessíveis; contar somente tempo ativo.

### my-tasks-03

Anterior: Expor ações permitidas de Iniciar, Pausar e Finalizar e abrir o detalhe, integrando o cronômetro segundo Gestão de Tempo. Não oferecer Retomar, Reabrir, Devolver à fila, Bloquear ou seletor manual de situação.

Proposto: Expor ações permitidas de Iniciar, Pausar e Finalizar e abrir o detalhe, integrando o cronômetro segundo Gestão de Tempo: pausa salva as horas e libera iniciar outra tarefa; novo início abre nova execução. Manter recorte pessoal inclusive para administradores. Não oferecer Retomar, Reabrir, Devolver à fila, Bloquear ou seletor manual de situação.

### manage-project-board-04

Anterior: Restringir consulta aos participantes e alterações aos autorizados; empilhar colunas em mobile e usar rótulos que não dependam só de cor.

Proposto: Participantes consultam seus projetos; administradores consultam qualquer projeto sem participação. Alterações seguem autorizações, inclusive Iniciar/Pausar/Finalizar exclusivos do responsável. Empilhar colunas em mobile e usar rótulos que não dependam só de cor.

### view-management-dashboard-01

Anterior: Restringir membros às próprias tarefas/horas e gestores à equipe nos projetos gerenciados; respeitar papéis por projeto.

Proposto: Restringir membros às próprias tarefas/horas e gestores à equipe nos projetos gerenciados; administradores podem consultar equipes e indicadores de todos os projetos. Respeitar os demais limites de situação e período.

### manage-task-12

Anterior: Aceitar anexos separados da descrição: PDF, imagens, documentos de texto, planilhas e ZIP, até 20 MB por arquivo. Participantes ativos podem adicionar/baixar, excluir somente próprios com confirmação; imagens também podem ser inseridas no editor da descrição e comentários.

Proposto: Aceitar anexos separados da descrição: PDF, imagens, documentos de texto, planilhas e ZIP, até 20 MB por arquivo. Participantes ativos e administradores podem adicionar/baixar, excluir somente próprios com confirmação; imagens também podem ser inseridas no editor da descrição e comentários.

### manage-task-13

Anterior: Finalizadas mantêm colaboração e atribuição, sem ações de situação. Canceladas ficam somente consulta exceto Arquivar por gestor; arquivadas permitem consulta/download e Desarquivar por gestor em projeto ativo. Projeto arquivado impede mutações.

Proposto: Finalizadas mantêm colaboração e atribuição, sem ações de situação. Canceladas ficam somente consulta exceto Arquivar por gestor do projeto ou administrador; arquivadas permitem consulta/download e Desarquivar por gestor do projeto ou administrador em projeto ativo. Projeto arquivado impede mutações.

## Verificação

Estado candidato validado; projeção gerada pelo renderizador do fluxo e comparada integralmente. Identidades, issues, artefatos, fontes, candidatos, grafo, ordem, relações e históricos preservados. A validação de transição com registro aprovado será executada após a resposta, sem fabricar aprovação.

Fingerprint do catálogo completo: 89759a4f2b30efdc34031fcc634de9df05328bbd7704229d7205a02d43d509b0.

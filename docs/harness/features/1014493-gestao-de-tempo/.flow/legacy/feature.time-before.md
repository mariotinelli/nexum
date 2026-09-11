# [WEB] [OPERACIONAL] Gestão de Tempo

Issue #1014493. Em coleta; requisito ainda não aprovado.

## Objetivo

Registrar, corrigir e consultar o esforço realizado nas tarefas, manualmente ou por cronômetro.

## Entrega herdada

Página de apontamentos e registros por tarefa/projeto, formulários manuais e cronômetro global persistente. Entrega totais de horas em detalhe/listas de projetos e tarefas e integra as restrições de execução aberta.

- Criar apontamento ligado a tarefa, usuário, data, duração positiva, descrição opcional e origem Manual/Cronômetro.
- Editar/excluir somente os próprios apontamentos, com confirmação; consultar registros da tarefa e projeto acessíveis, sem aprovação de horas.
- Filtrar por projeto, pessoa e período, paginar e somar a duração do período; apresentar modal e cards mobile.
- Iniciar execução autorizada, pausar e voltar a iniciar, exibir tempo e tarefa globalmente e impedir outra execução aberta, incluindo pausada. Respeitar as ações e permissões da Gestão de Tarefa, sem oferecer edição direta de situação.
- Finalizar criando apontamento com origem Cronômetro ou descartar com confirmação; manter contagem correta após recarregar ou fechar a página.
- Integrar o cronômetro às ações de tarefa já entregues, respeitando o novo fluxo e suas permissões; exigir finalizar/descartar execução aberta antes de Finalizar ou Arquivar a tarefa, quando a ação for permitida, e antes de arquivar o projeto. Gestão de Tarefa funciona sem exigir cronômetro; detalhes da integração pertencem à entrevista de Gestão de Tempo.
- Atualizar horas realizadas pela soma dos apontamentos em tarefa, projeto e suas consultas; tarefas canceladas/arquivadas e projetos arquivados permitem consulta e impedem mutações.
- Tratar tarefa não autorizada, duração inválida, execução já aberta, vazio e erros acessíveis; detalhes de arredondamento ficam para a entrevista.
- Registrar esforço sem aprovação de apontamentos, faturamento ou centros de custo; nenhum apontamento depende de integração com sistema externo.

## Dependência

Gestão de Tarefa (#1014454). Relação nativa 666 criada e conferida: Gestão de Tarefa bloqueia Gestão de Tempo. Entrevista em andamento.

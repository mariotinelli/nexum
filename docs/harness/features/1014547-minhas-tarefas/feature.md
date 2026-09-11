# [WEB] [OPERACIONAL] Minhas Tarefas

Issue: #1014547.

## Objetivo

Permitir que o usuário ativo organize e execute suas próprias responsabilidades pela interface WEB em português, encontrando tarefas por execução e prazo, refinando a consulta e acionando o cronômetro sem sair da lista. A visão mantém o recorte pessoal para todos os perfis, inclusive administradores, e respeita as regras aprovadas de tarefa e tempo.

## Resultado esperado

Encontrar o trabalho atual em seis grupos exclusivos, iniciar, pausar ou finalizar tarefas permitidas e acompanhar a atualização da lista e do cronômetro. Consultar também as tarefas finalizadas hoje e nos seis dias corridos anteriores. Filtros, ordenação e paginação preservam o contexto durante o acesso atual.

## Atores e permissões

- Usuário autenticado e ativo, seja membro, gestor ou administrador: consulta somente tarefas atribuídas a si, dentro do acesso vigente aos projetos.
- Administradores mantêm o alcance administrativo aprovado, mas Minhas Tarefas não apresenta atribuições alheias.
- Excluir tarefas Canceladas, Arquivadas e todas as tarefas de projetos arquivados. A consulta histórica continua nos locais previstos pelas outras capacidades.
- Iniciar, Pausar e Finalizar são exclusivos do responsável atual e exigem projeto ativo e transição válida. Revalidar permissões em cada ação, inclusive em telas já abertas.
- Nova tarefa apenas encaminha ao cadastro existente para quem tem permissão de criação conforme Gestão de Tarefa. Não concede permissões nem atribui automaticamente a tarefa ao usuário.

## Histórias de usuário

1. Como responsável, quero ver somente minhas tarefas para organizar meu trabalho pessoal.
2. Como responsável, quero localizar execução atual, atrasos e prazos sem encontrar a mesma tarefa em vários grupos.
3. Como responsável, quero consultar minhas finalizações recentes para acompanhar as entregas da última semana.
4. Como responsável, quero combinar busca e filtros para encontrar uma tarefa específica.
5. Como responsável, quero ordenar e paginar cada grupo para percorrer suas tarefas.
6. Como responsável, quero abrir detalhes e voltar ao mesmo contexto para continuar a consulta.
7. Como responsável, quero Iniciar, Pausar e Finalizar diretamente na lista para executar o trabalho e registrar o tempo.
8. Como responsável, quero ver os grupos e contadores atualizados após minhas ações, mantendo os filtros.
9. Como pessoa autorizada a criar tarefas, quero abrir o cadastro existente pela página.
10. Como usuário, quero consultar os mesmos dados e usar as ações essenciais em desktop e mobile, com retorno claro das operações.

## Fluxo principal

**Entrada:** abrir Minhas Tarefas. Sem contexto preservado, usar busca e prazo vazios, todos os projetos ativos acessíveis, todas as situações elegíveis e prioridades, Apenas atrasadas desmarcado, criação mais recente e primeira página de cada grupo. O responsável é sempre o usuário conectado; não oferecer seleção de outra pessoa.

**Agrupamento:** aplicar busca e filtros ao conjunto permitido e distribuir cada tarefa uma única vez, na ordem abaixo. Manter os seis grupos visíveis, inclusive com contador zero e mensagem de vazio.

| Grupo | Conteúdo |
| --- | --- |
| Em execução | Tarefa Em andamento; precede o agrupamento por prazo e mantém eventual aviso de atraso |
| Atrasadas | Pendentes ou Pausadas com prazo anterior a hoje |
| Para hoje | Pendentes ou Pausadas com prazo igual a hoje |
| Próximas | Pendentes ou Pausadas com qualquer prazo futuro |
| Sem prazo | Pendentes ou Pausadas sem prazo |
| Finalizadas recentemente | Finalizadas entre hoje menos seis dias corridos e hoje, inclusive, pela data de finalização |

Usar o horário de Brasília para determinar hoje e a data da finalização. Fins de semana, feriados e férias não alteram a janela. Uma Finalizada fora da janela não aparece em outro grupo, mesmo com prazo vencido ou ausente.

**Busca e filtros:** pesquisar trecho em título ou descrição, ignorando maiúsculas/minúsculas, acentos e espaços nas extremidades. Combinar projeto, situação, prioridade, Prazo até e Apenas atrasadas por E. Projeto, situação e prioridade têm seleção única e opção geral. Situações disponíveis: Pendente, Em andamento, Pausada e Finalizada. Prioridades: Baixa, Média, Alta e Urgente. Acionar Aplicar filtros para efetivar a consulta e reiniciar as páginas dos grupos. Um filtro nunca amplia o conjunto pessoal nem recupera finalizadas fora da janela.

**Prazo e atraso:** Prazo até inclui a data informada e exclui tarefas sem prazo. Apenas atrasadas exige prazo anterior a hoje e situação Pendente, Em andamento ou Pausada. Uma tarefa Em andamento atrasada continua em Em execução, com aviso de atraso; Finalizadas nunca são atrasadas.

**Ordenação e paginação:** ordenar dentro de cada grupo por criação mais recente como padrão. Oferecer atualização mais recente, prazo crescente com sem prazo por último e prioridade Urgente, Alta, Média e Baixa. Empates usam criação mais recente. Cada grupo tem oito tarefas por página, total filtrado e Anterior/Próxima independentes; navegar em um grupo preserva as páginas dos demais. A ordenação não muda a sequência dos grupos.

**Detalhe e continuidade:** abrir o detalhe pelo título. Ao voltar, navegar ou recarregar durante o acesso atual, preservar filtros, ordenação e páginas, em contexto separado da Consulta de Tarefas. Limpar restaura valores iniciais e primeiras páginas. Sair e entrar novamente também restaura o padrão. Se uma página deixar de existir, usar a última disponível do respectivo grupo; sem resultados, mostrar o grupo vazio.

**Execução:** apresentar somente ações permitidas pela situação: Pendente ou Pausada permite Iniciar e Finalizar; Em andamento permite Pausar e Finalizar; Finalizada não permite ações de situação. Iniciar abre uma nova execução de cronômetro. Pausar salva o tempo, encerra a execução e deixa a tarefa Pausada, permitindo iniciar outra tarefa. Finalizar salva somente tempo ainda não registrado e torna a tarefa Finalizada, sem duplicar apontamentos anteriores ou exigir encerramento separado do cronômetro. Aplicar integralmente as regras da Gestão de Tempo, inclusive limite de oito horas por execução, pausa automática, precisão e virada de dia.

**Resultado da ação:** após sucesso, atualizar situação, grupo e contadores sem sair de Minhas Tarefas. A tarefa pode mudar de grupo ou deixar de aparecer pelos filtros. Preservar contexto e páginas válidas, usando a última disponível quando necessário. O cronômetro global permanece visível mesmo quando sua tarefa não corresponde aos filtros.

**Nova tarefa:** quem tem permissão aciona o botão e abre o cadastro da Gestão de Tarefa. Cadastro, cancelamento e resultado seguem o fluxo existente; entrar por Minhas Tarefas não cria atribuição automática.

## Fluxos alternativos e exceções

- Nenhuma tarefa própria ou filtros sem correspondência: manter grupos vazios, contadores zero e possibilidade de limpar filtros.
- Combinar Finalizada com Apenas atrasadas: nenhum resultado; não alterar as regras para preencher grupos.
- Outro cronômetro rodando: impedir novo início e informar a execução existente, conforme Gestão de Tempo. Pausar a execução atual salva e libera outro início.
- Perda de responsabilidade ou acesso, conta inativa, projeto arquivado ou situação alterada após a consulta: impedir ação indevida e informar o motivo; a nova consulta respeita a condição vigente.
- Alteração de vínculo durante execução: aplicar a pausa automática e preservação de horas já aprovadas em Gestão de Tempo, sem conceder controle manual a terceiros.
- Finalizar sem tempo contado: finalizar a tarefa sem apontamento zero e sem afetar o cronômetro de outra tarefa.
- Falha ou indisponibilidade: mostrar mensagem e permitir nova tentativa com o contexto preservado, sem anunciar sucesso nem duplicar operação já concluída.
- Página deixa de existir após uma ação ou mudança dos resultados: ajustar somente o grupo afetado para sua última página, ou exibir vazio.

## Regras de negócio

R1. A lista é pessoal para todos os perfis. Excluir Canceladas, Arquivadas e tarefas de projetos arquivados; aplicar acesso vigente e conta ativa.

R2. Cada tarefa aparece em exatamente um dos seis grupos elegíveis. Em execução prevalece sobre prazo, sem ocultar atraso; Pendentes e Pausadas são distribuídas por prazo. Manter ordem e grupos vazios.

R3. Finalizadas recentemente abrange hoje e os seis dias corridos anteriores, inclusive, pela data de finalização em Brasília. Não considerar dias úteis, feriados ou férias no cálculo. Finalizadas mais antigas ficam fora desta página.

R4. A busca corresponde a trecho do título ou descrição e ignora caixa, acentos e espaços nas extremidades. Filtros preenchidos são cumulativos; o responsável permanece fixo no usuário. Aplicar filtros reinicia as páginas; filtros não mudam a elegibilidade de R1–R3.

R5. Prazo até é inclusivo e exclui sem prazo. Atraso exige prazo anterior a hoje e situação Pendente, Em andamento ou Pausada. Finalizada, prazo de hoje, futuro ou ausente não constitui atraso.

R6. Ordenação interna por criação decrescente como padrão, atualização decrescente, prazo crescente com sem prazo no fim ou prioridade Urgente→Baixa. Empates pela criação mais recente. Oito tarefas por página de cada grupo; contadores consideram todos os resultados filtrados desse grupo.

R7. Preservar filtros, ordenação e páginas durante o acesso atual, inclusive retorno do detalhe e recarga, sem compartilhar contexto com Consulta de Tarefas. Limpar ou novo login restaura padrão. Página inexistente passa à última disponível do grupo.

R8. Iniciar/Pausar/Finalizar respeitam responsabilidade, projeto ativo, situações e integração aprovadas em Gestão de Tarefa e Gestão de Tempo. Não há Retomar, Reabrir, Devolver à fila, Bloquear, Descartar nem seletor manual de situação nesta página.

R9. Sucesso atualiza grupos e contadores sem sair da tela, preservando filtros e páginas válidas. Cronômetro global independe dos filtros. Falha não anuncia sucesso nem duplica trabalho já registrado.

R10. Detalhe e Nova tarefa são navegação para capacidades existentes, com suas permissões. Cards mostram dados essenciais e ações válidas em desktop/mobile; criação não atribui automaticamente a tarefa ao usuário.

## Dados percebidos pelo usuário

Busca, projeto, situação, prioridade, Prazo até, Apenas atrasadas, ordenação, Aplicar filtros e Limpar. Seis grupos com total filtrado, vazio e paginação independente. Cards com título e acesso ao detalhe, projeto, situação, prioridade, prazo ou Sem prazo, aviso de atraso e ações permitidas. Cronômetro global com tarefa e tempo; Nova tarefa conforme permissão. Mensagens de carregamento, vazio, erro, indisponibilidade e sucesso.

## Critérios de aceite

CA1 — Como membro, gestor ou administrador ativo, ao abrir Minhas Tarefas, mostrar somente tarefas próprias acessíveis. Excluir tarefas alheias, Canceladas, Arquivadas e de projetos arquivados. [R1]

CA2 — Com tarefa Em andamento e prazo vencido, ao consultar, mostrá-la apenas em Em execução com aviso de atraso, sem duplicá-la em Atrasadas. [R2, R5]

CA3 — Com Pendentes e Pausadas de prazo passado, hoje, futuro ou ausente, ao consultar, distribuí-las respectivamente em Atrasadas, Para hoje, Próximas e Sem prazo. Manter seis grupos na ordem fixa, inclusive vazios. [R2]

CA4 — Com hoje em 10/09/2026, ao consultar finalizações, incluir datas de 04/09/2026 a 10/09/2026 em Brasília e excluir 03/09/2026 e anteriores. Incluir finais de semana, feriados e dias de férias dentro da janela. Usar data de finalização, não prazo da tarefa. [R3]

CA5 — Com uma Finalizada fora da janela e prazo vencido ou ausente, ao consultar ou filtrar Finalizada, não colocá-la em nenhum grupo. Uma Finalizada elegível aparece somente em Finalizadas recentemente. [R2–R4]

CA6 — Com “Revisão do contrato” no título de uma tarefa própria e na descrição de outra, ao buscar “ revisao ” e aplicar, encontrar ambas quando satisfazem os demais filtros. Texto vazio não restringe. [R4]

CA7 — Com projeto, situação, prioridade e demais filtros preenchidos, ao Aplicar filtros, exigir todas as condições e voltar à primeira página de cada grupo. Não oferecer seleção de outro responsável nem situações excluídas. [R1, R4]

CA8 — Ao informar Prazo até, incluir prazo igual ou anterior e excluir posterior ou ausente. Ao marcar Apenas atrasadas, incluir somente Pendentes, Em andamento ou Pausadas com prazo anterior a hoje, mantendo a precedência de Em execução. [R2, R5]

CA9 — Ao combinar Finalizada e Apenas atrasadas ou outra combinação sem correspondência, apresentar grupos vazios e contadores zero; Limpar restaura a consulta padrão. [R4–R5, R7]

CA10 — Ao selecionar cada ordenação, ordenar dentro dos grupos conforme criação/atualização decrescente, prazo crescente ou prioridade Urgente→Baixa, com criação mais recente nos empates; manter a sequência dos grupos. [R6]

CA11 — Com mais de oito tarefas filtradas em dois grupos, ao avançar em um, mostrar até oito por página e preservar a página do outro. Contador de cada grupo representa todo o seu resultado filtrado. [R6]

CA12 — Após abrir detalhe e voltar, navegar ou recarregar, preservar filtros, ordenação e páginas de Minhas Tarefas; alterações na Consulta de Tarefas não sobrescrevem esse contexto. Sair e entrar novamente ou Limpar restaura os valores iniciais. [R7]

CA13 — Como responsável de tarefa Pendente ou Pausada de projeto ativo, ao Iniciar sem outro cronômetro rodando, mudar para Em andamento, abrir nova execução e mover para Em execução quando corresponde aos filtros. Com outro cronômetro rodando, recusar e informar. [R8–R9]

CA14 — Com tarefa em execução, ao Pausar, salvar o tempo, encerrar a execução, deixar Pausada e atualizar seu grupo conforme prazo e filtros. Permitir iniciar outra tarefa sem finalizar a anterior; novo início respeita novo limite de oito horas. [R8–R9]

CA15 — Como responsável de Pendente, Em andamento ou Pausada, ao Finalizar, registrar data/hora e salvar somente tempo ainda não registrado. Atualizar situação, grupos e contadores sem duplicar apontamentos anteriores; sem tempo contado, não criar registro zero. [R8–R9]

CA16 — Após ação que faz a tarefa deixar de corresponder aos filtros, removê-la dos resultados e atualizar contadores, mantendo filtros. Se a página do grupo deixar de existir, abrir sua última disponível; preservar as páginas válidas dos demais grupos. [R7, R9]

CA17 — Com cronômetro rodando em tarefa excluída pelos filtros, ao aplicar a consulta, manter o cronômetro global e seus controles autorizados visíveis. [R9]

CA18 — Com atribuição, acesso, situação ou estado do projeto alterado desde a consulta, ao tentar ação não mais permitida, recusar e informar o motivo. Perda de vínculo durante contagem aplica a pausa e registro previstos em Gestão de Tempo. [R1, R8]

CA19 — Com tarefa Finalizada, ao consultar o card, não oferecer ação de situação. Não apresentar Retomar, Reabrir, Bloquear, Devolver à fila, Descartar ou seletor manual em outros estados. [R8]

CA20 — Em falha de consulta ou ação, apresentar erro e permitir nova tentativa preservando contexto; não anunciar sucesso nem duplicar operação concluída. [R9; exceções]

CA21 — Como pessoa autorizada a criar, ao acionar Nova tarefa, abrir o cadastro existente sem atribuição automática. Pessoa sem permissão não obtém criação por esta página; título da tarefa abre o detalhe autorizado. [R10]

CA22 — Em desktop/mobile, ao consultar cards, filtros, grupos e paginação, apresentar os dados essenciais e ações acessíveis por teclado, com labels, foco e mensagens. Distinguir carregamento, vazio, erro e sucesso e manter alvos de toque adequados. [R10; guia]

## Dependências

Gestão de Tempo (#1014493), com relação nativa 667 criada e conferida: #1014493 bloqueia #1014547. Fornece cronômetro, registro de horas e integração das ações. Gestão de Tarefa (#1014454) fornece dados, atribuição, situações, prioridades, prazo, detalhe e cadastro por essa cadeia. Projetos e contas fornecem acesso e estados vigentes conforme requisitos anteriores.

Consulta de Tarefas (#1014465) é referência de consistência para busca e filtros; sua consulta transversal e seu contexto permanecem separados. Esta Feature não redefine permissões nem regras centrais do cronômetro.

## Designs e evidências

- [Minhas tarefas](../../scopes/2026-09-09-nexum-scope/sources/design-my-tasks.md) e [guia de design](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md), incluindo F07, F09 e F14.
- [Entrevista](history/interview.md): Q96, Q98–Q105 e confirmação explícita do entendimento por Mário Tinelli. Q103 substitui Q97: hoje e seis dias corridos anteriores.
- [Catálogo revisado aprovado](../../scopes/2026-09-09-nexum-scope/.flow/reviews/catalog-time-review.md), convenção e limites herdados.
- O protótipo mostrava finalizadas sem limite de data e grupos sem paginação. Q103 define a janela; Q100 define oito por grupo. Q96 define exclusões; Q98 amplia a busca para título ou descrição. Referências antigas de situação, reabertura e descarte são substituídas pelas regras já aprovadas de Tarefa/Tempo.

## Dentro do escopo

Visão pessoal agrupada, janela de finalizações, busca, filtros, ordenação, paginação independente, preservação de contexto, navegação para detalhe/cadastro e execução integrada às capacidades aprovadas. Interface WEB responsiva em português com estados de carregamento, vazio, erro, indisponibilidade e sucesso. Aplicam-se os requisitos explícitos do guia: contraste WCAG AA, teclado, foco visível, labels, nomes acessíveis, informação sem depender apenas de cor, alvos de toque, hierarquia semântica e redução de movimento.

## Fora do escopo

Consulta de tarefas alheias, histórico fora da janela nesta página, tarefas canceladas/arquivadas e de projetos arquivados, calendário de dias úteis/feriados/férias, novas permissões, atribuição automática, edição de dados ou seletor de situação nos cards. Cadastro, detalhe, colaboração, apontamentos manuais e regras centrais de tarefa/cronômetro pertencem às capacidades responsáveis. Sem novas transições, aplicativo nativo, API pública, notificações ou integração externa.

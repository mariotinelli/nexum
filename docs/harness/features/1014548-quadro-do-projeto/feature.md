# [WEB] [OPERACIONAL] Quadro do Projeto

Issue: #1014548.

## Objetivo

Permitir que participantes e administradores acompanhem visualmente o fluxo de tarefas de um projeto e executem ações autorizadas nos cards pela interface WEB em português. O quadro reúne situação, responsabilidade, prazo e esforço, preservando as regras aprovadas de Gestão de Tarefa e Gestão de Tempo.

## Resultado esperado

Consultar as tarefas não arquivadas do projeto em cinco colunas, percorrê-las com paginação independente, abrir detalhes e executar transições válidas sem sair do quadro. As operações atualizam cards e contadores, preservando o contexto de navegação. Projetos arquivados mantêm o quadro somente para consulta.

## Atores e permissões

- Participantes autenticados e ativos consultam o quadro dos projetos dos quais participam.
- Administradores ativos consultam qualquer projeto, mesmo sem participação.
- Somente o responsável atual pode Iniciar, Pausar ou Finalizar uma tarefa, inclusive quando gestor ou administrador.
- Gestores do projeto e administradores podem Cancelar e Arquivar nas situações permitidas pela Gestão de Tarefa.
- Nova tarefa fica disponível somente para quem pode criar naquele projeto ativo, conforme o cadastro existente.
- Projeto arquivado impede todas as mutações pelo quadro, inclusive para administradores, mantendo consulta e navegação autorizada ao detalhe.
- Validar conta, acesso, responsabilidade, situação e estado do projeto em cada ação, inclusive após mudanças ocorridas com a tela aberta. O quadro não concede permissões adicionais.

## Histórias de usuário

1. Como participante ou administrador, quero ver as tarefas do projeto separadas por situação para acompanhar seu fluxo.
2. Como usuário autorizado, quero consultar responsável, prioridade, prazo, estimativa e horas realizadas nos cards para compreender cada tarefa.
3. Como usuário autorizado, quero percorrer as colunas com paginação independente para consultar todo o quadro.
4. Como usuário autorizado, quero abrir o detalhe e voltar ao mesmo contexto para continuar a análise.
5. Como responsável, quero Iniciar, Pausar e Finalizar pelo card para executar meu trabalho e registrar tempo.
6. Como gestor do projeto ou administrador, quero Cancelar e Arquivar tarefas permitidas para administrar seu ciclo de vida.
7. Como usuário autorizado, quero ver os resultados das ações refletidos no quadro sem perder minhas páginas.
8. Como pessoa autorizada a criar, quero abrir o cadastro com o projeto atual preenchido para adicionar uma tarefa ao contexto em análise.
9. Como usuário autorizado, quero consultar o quadro de um projeto arquivado sem alterar seus registros.
10. Como usuário, quero consultar cards e operar ações em desktop e mobile, com retorno claro de carregamento, vazio, sucesso ou falha.

## Fluxo principal

**Entrada contextual:** abrir o quadro de um projeto a partir da navegação existente. Identificar o projeto no cabeçalho e aplicar suas permissões vigentes. Sem contexto preservado, começar na primeira página de cada coluna.

**Colunas:** apresentar, nesta ordem, Pendente, Em andamento, Pausada, Finalizada e Cancelada. Cada tarefa não arquivada do projeto aparece somente na coluna de sua situação atual. Manter as cinco colunas, inclusive vazias, com contador do total e mensagem de vazio. Finalizadas não têm limite de período; o quadro não aplica o recorte pessoal nem a janela de Minhas Tarefas. Tarefas arquivadas não entram nas colunas ou contadores.

**Cards:** apresentar título com acesso ao detalhe, responsável ou Sem responsável, prioridade, prazo ou Sem prazo, indicador de atraso, estimativa e horas realizadas. Utilizar os dados e a apresentação de esforço definidos nas capacidades existentes. Horas realizadas correspondem aos apontamentos salvos; tempo ainda em contagem não é somado como apontamento.

**Ordenação e paginação:** usar ordem fixa de criação mais recente primeiro dentro de cada coluna, sem controle de ordenação. Mostrar oito tarefas por página em cada coluna, com Anterior/Próxima independentes e contador do total da coluna, não apenas da página. Navegar em uma coluna preserva as páginas das demais.

**Detalhe e continuidade:** abrir o detalhe pelo título do card. Ao retornar ou recarregar durante o acesso atual, preservar as páginas separadamente por projeto. Visitar outro projeto não sobrescreve o contexto do anterior; projeto sem contexto começa nas primeiras páginas. Sair e entrar novamente restaura o padrão. Se uma página deixar de existir devido a mudanças nos resultados, abrir a última disponível da respectiva coluna; sem tarefas, apresentar vazio.

**Ações:** disponibilizar somente as combinações abaixo, condicionadas à autorização e a projeto ativo. O quadro não oferece seletor de situação nem arraste que a altere.

| Situação | Ações e resultados |
| --- | --- |
| Pendente | Iniciar → Em andamento; Finalizar → Finalizada; Cancelar → Cancelada; Arquivar → Arquivada |
| Em andamento | Pausar → Pausada; Finalizar → Finalizada |
| Pausada | Iniciar → Em andamento; Finalizar → Finalizada; Cancelar → Cancelada; Arquivar → Arquivada |
| Finalizada | Nenhuma ação de situação |
| Cancelada | Arquivar → Arquivada |

Iniciar/Pausar/Finalizar são exclusivos do responsável; Cancelar/Arquivar exigem gestor do projeto ou administrador. Finalizar registra data/hora conforme Gestão de Tarefa. Arquivar exige confirmação: confirmar arquiva e retira o card; cancelar preserva a tarefa.

**Integração de tempo:** Iniciar abre nova execução de cronômetro; Pausar salva o tempo e encerra a execução, deixando Pausada e liberando o início de outra tarefa. Finalizar salva somente o tempo ainda não registrado e finaliza a tarefa, sem duplicar pausas anteriores nem exigir encerramento separado. Sem tempo contado, não criar apontamento zero. Aplicar as regras aprovadas de Gestão de Tempo, inclusive uma contagem por pessoa, limite de oito horas por execução, precisão, virada de dia e pausa automática por perda de vínculo. O cronômetro global segue disponível independentemente da página ou coluna em que seu card esteja.

**Resultado:** após uma ação bem-sucedida, atualizar situação, horas salvas e contadores sem sair do quadro. Mover o card para sua coluna atual ou removê-lo após Arquivar. Respeitar a ordenação e preservar as páginas válidas; se uma página desaparecer, usar a última disponível daquela coluna. Não navegar automaticamente até a página de destino do card movido. As demais colunas mantêm seu contexto.

**Nova tarefa:** oferecer o botão apenas a quem pode criar naquele projeto ativo. Ao acioná-lo, abrir o cadastro existente com o projeto atual preenchido, preservando suas opções e permissões. Não bloquear a troca de projeto além das regras do cadastro e não atribuir automaticamente o responsável. Validações, cancelamento e resultado seguem Gestão de Tarefa.

**Projeto arquivado:** mostrar indicação de somente consulta. Permitir percorrer colunas e abrir detalhes autorizados, sem Nova tarefa ou ações de mutação nos cards.

## Fluxos alternativos e exceções

- Projeto sem tarefas não arquivadas: manter cinco colunas vazias, contadores zero e navegação permitida.
- Coluna sem tarefas: mostrar vazio e não oferecer avanço sem página disponível.
- Usuário sem acesso, conta inativa ou perda de participação sem acesso administrativo: impedir consulta restrita, inclusive por acesso direto.
- Situação, responsável ou estado do projeto mudou desde a consulta: revalidar e recusar ação agora indevida, com mensagem; não aplicar a transição antiga.
- Tarefa sem responsável: não permitir Iniciar/Pausar/Finalizar. Gestores e administradores mantêm somente suas ações válidas de Cancelar/Arquivar.
- Outro cronômetro rodando para a pessoa: recusar novo início e informar a execução existente. Pausar a execução atual salva e libera outro início, conforme Gestão de Tempo.
- Finalizada: não permitir ações de situação, inclusive Arquivar ou Reabrir. Cancelada: permitir somente Arquivar por pessoa autorizada.
- Cancelar a confirmação de Arquivar: preservar card, situação e contadores.
- Perda de vínculo durante contagem: aplicar a pausa automática e preservação das horas já aprovadas, sem conceder controle manual a terceiros.
- Falha de carregamento, ação ou indisponibilidade: mostrar mensagem e permitir nova tentativa preservando o contexto, sem anunciar sucesso ou duplicar operação já concluída.

## Regras de negócio

R1. O quadro pertence a um projeto. Participantes consultam seus projetos; administradores consultam qualquer projeto. Conta ativa e acesso vigente são exigidos inclusive em acessos diretos.

R2. As cinco colunas são fixas e seguem a situação atual. Tarefas arquivadas são excluídas; Finalizadas e Canceladas permanecem sem limite de período. Cada tarefa aparece uma vez. Colunas vazias permanecem visíveis.

R3. Cards mostram título/link, responsável, prioridade, prazo/atraso, estimativa e horas realizadas. Atraso exige prazo anterior a hoje e situação Pendente, Em andamento ou Pausada. Finalizada e Cancelada não são atrasadas. Totais de esforço usam apontamentos salvos, conforme Gestão de Tempo.

R4. Ordenar por criação decrescente, sem controle de ordenação. Cada coluna tem oito tarefas por página, controles independentes e contador de todas as suas tarefas elegíveis.

R5. Preservar páginas por projeto ao voltar do detalhe e recarregar até sair da conta. Contexto de um projeto não sobrescreve outro. Novo login ou projeto sem contexto começa nas primeiras páginas; página inexistente passa à última disponível da coluna.

R6. Ações obedecem à tabela e às permissões de Gestão de Tarefa. Somente o responsável executa Iniciar/Pausar/Finalizar; gestor do projeto ou administrador executa Cancelar/Arquivar nas origens válidas. Arquivar exige confirmação. Não existe seletor de situação nem arraste que a altere.

R7. Execução e apontamentos seguem Gestão de Tempo: uma contagem por pessoa, pausa que salva e encerra, novo início com novo limite de oito horas e finalização integrada sem duplicação. Não existe Descartar. O quadro consome essas regras, sem modificá-las.

R8. Sucesso atualiza cards, horas salvas e contadores no lugar, respeitando situação, ordenação e páginas. Card movido não força navegação até sua página. Falha não anuncia sucesso nem duplica operação concluída.

R9. Projeto arquivado permite somente consulta para todos os perfis. Revalidar autorização e estado em cada ação; botões visíveis anteriormente não mantêm permissão.

R10. Nova tarefa abre o cadastro existente com projeto atual preenchido e permissões preservadas, sem atribuição automática. Detalhes, cadastro e demais operações fora dos cards permanecem nas capacidades responsáveis.

## Dados percebidos pelo usuário

Cabeçalho com projeto, indicação de somente consulta quando arquivado, cinco colunas com situação e contagem total, cards, paginação por coluna, acesso ao detalhe e Nova tarefa conforme permissão. Ações válidas e confirmação de Arquivar; cronômetro global. Mensagens de carregamento, vazio, erro, indisponibilidade e sucesso. No mobile, colunas empilhadas com rótulos completos e ações adequadas para toque.

## Critérios de aceite

CA1 — Como participante ativo, ao abrir o quadro, permitir somente projetos acessíveis. Como administrador ativo, permitir qualquer projeto mesmo sem participação. Conta inativa ou usuário sem acesso não consulta conteúdo restrito por URL direta. [R1]

CA2 — Com tarefas nas cinco situações, ao abrir, apresentar Pendente, Em andamento, Pausada, Finalizada e Cancelada nessa ordem, cada tarefa uma vez. Excluir Arquivadas dos cards e contadores; incluir Finalizadas antigas sem janela de data. [R2]

CA3 — Com projeto ou coluna sem tarefas elegíveis, ao consultar, manter todas as colunas, mensagens de vazio e contadores zero correspondentes. [R2]

CA4 — Ao consultar um card, apresentar título/link, responsável ou Sem responsável, prioridade, prazo ou Sem prazo, estimativa e horas realizadas. Pendentes, Em andamento e Pausadas com prazo anterior a hoje recebem atraso; Finalizadas e Canceladas não. [R3]

CA5 — Com cronômetro contando e apontamentos anteriores salvos, ao consultar horas realizadas, apresentar a soma dos registros salvos sem incorporar tempo ainda em contagem. Após pausa bem-sucedida pelo card, refletir as horas registradas. [R3, R7–R8]

CA6 — Com mais de oito tarefas em duas colunas, ao abrir e navegar, ordenar por criação mais recente e mostrar até oito por página. Avançar em uma preserva a outra; contador representa o total da coluna. Não oferecer controle de ordenação. [R4]

CA7 — Após navegar nas páginas de dois projetos, ao abrir detalhe e voltar ou recarregar, preservar o contexto de cada projeto. Após sair e entrar novamente, iniciar nas primeiras páginas. [R5]

CA8 — Como responsável de Pendente ou Pausada em projeto ativo, ao Iniciar sem outro cronômetro rodando, mudar para Em andamento e iniciar nova execução. Pessoa não responsável é impedida, mesmo sendo gestor ou administrador. [R6–R7]

CA9 — Com outra contagem rodando para a pessoa, ao tentar Iniciar, recusar e informar a execução existente. Após Pausar a atual, salvar e encerrar a execução, permitindo iniciar outra tarefa. [R7]

CA10 — Como responsável de Em andamento, ao Pausar, deixar Pausada, salvar tempo, atualizar horas e contadores e mover o card respeitando a página e ordenação de destino. Novo início abre outra execução com limite próprio. [R6–R8]

CA11 — Como responsável de Pendente, Em andamento ou Pausada, ao Finalizar, tornar Finalizada com data/hora e salvar somente tempo ainda não registrado. Não duplicar pausas anteriores nem criar apontamento zero quando não houver tempo contado. [R6–R8]

CA12 — Como gestor do projeto ou administrador, ao Cancelar Pendente ou Pausada, tornar Cancelada e atualizar o quadro. Recusar Cancelar Em andamento, Finalizada ou Cancelada e recusar a ação a membro sem permissão de gestão. [R6]

CA13 — Como gestor do projeto ou administrador, ao Arquivar Pendente, Pausada ou Cancelada, pedir confirmação. Confirmar retira card e atualiza contadores; cancelar preserva os dados. Recusar Arquivar Em andamento ou Finalizada. [R2, R6, R8]

CA14 — Com Finalizada, ao consultar, não oferecer ação de situação. Com Cancelada, oferecer somente Arquivar à pessoa autorizada. Sem responsável, impedir Iniciar/Pausar/Finalizar e manter apenas outras ações autorizadas. [R6]

CA15 — Após ação que move ou remove o último card de uma página, atualizar contadores e usar a última página disponível daquela coluna; preservar páginas válidas das demais. Não forçar navegação até a página do card movido. [R4–R5, R8]

CA16 — Com projeto arquivado, ao abrir o quadro como participante ou administrador, permitir paginação e detalhe em somente consulta. Não oferecer Nova tarefa nem ações de mutação. [R9]

CA17 — Com responsabilidade, acesso, situação ou estado do projeto alterado desde a exibição, ao tentar ação agora inválida, recusar e explicar. Perda de vínculo durante execução aplica a pausa e preservação de horas definidas em Gestão de Tempo. [R6–R7, R9]

CA18 — Como pessoa com permissão de criar no projeto ativo, ao acionar Nova tarefa, abrir cadastro com projeto atual preenchido, mantendo opções permitidas e sem atribuição automática. Pessoa sem permissão não obtém criação pelo quadro. [R10]

CA19 — Em falha de consulta ou ação, mostrar mensagem e permitir nova tentativa preservando contexto, sem falso sucesso nem duplicação. Cancelar a confirmação de Arquivar preserva o card e contadores. [R6, R8]

CA20 — Em desktop/mobile, ao consultar colunas, cards e paginação, apresentar os mesmos dados e ações essenciais; no mobile, empilhar colunas. Usar rótulos, teclado, foco e mensagens acessíveis sem depender apenas de cor. [Dados percebidos; guia]

## Dependências

Gestão de Tempo (#1014493), com relação nativa 668 criada e conferida: #1014493 bloqueia #1014548. Fornece horas realizadas, cronômetro e integração das ações. Gestão de Tarefa (#1014454) fornece situações, transições, autorização, dados, detalhe e cadastro por essa cadeia. Gestão de Projeto e conta ativa determinam acesso e somente consulta conforme capacidades anteriores.

## Designs e evidências

- [Quadro do projeto](../../scopes/2026-09-09-nexum-scope/sources/design-board.md) e [guia](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md), incluindo F08 e integração F09.
- [Entrevista](history/interview.md): Q106–Q110 e confirmação explícita do entendimento por Mário Tinelli.
- [Catálogo revisado aprovado](../../scopes/2026-09-09-nexum-scope/.flow/reviews/catalog-time-review.md): cinco situações, ações e alcance administrativo herdados.
- O protótipo antigo de quatro colunas e seletor de situação é substituído pelo catálogo e regras aprovadas. Q106 fixa criação decrescente; Q107 define oito cards por coluna; Q108 define preenchimento contextual do cadastro; Q109 preserva páginas por projeto; Q110 define atualização sem navegação forçada.

## Dentro do escopo

Quadro contextual por projeto, cinco colunas, cards e contagens, ordenação fixa, paginação independente, preservação por projeto, navegação para detalhe/cadastro e ações autorizadas integradas a tarefa/tempo. Somente consulta em projeto arquivado. Interface WEB responsiva em português com estados de carregamento, vazio, erro, indisponibilidade e sucesso. Aplicam-se as exigências explícitas do guia: contraste WCAG AA, teclado, foco visível, labels, nomes acessíveis, rótulos sem depender só de cor, alvos de toque, hierarquia semântica e redução de movimento.

## Fora do escopo

Filtros ou controles de ordenação no quadro, consulta transversal, recorte pessoal ou janela de finalizadas, tarefas arquivadas, edição direta de situação, arraste que a altere e novas transições. Não oferecer Retomar, Reabrir, Devolver à fila, Bloquear ou Descartar. Edição completa, atribuição, colaboração, cadastro e apontamentos manuais permanecem nas capacidades responsáveis, acessíveis pela navegação autorizada. Sem aplicativo nativo, API pública, notificações ou integrações externas.

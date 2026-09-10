# [WEB] [OPERACIONAL] Gestão de Tempo

Issue: #1014493.

## Objetivo

Permitir registrar, corrigir e consultar o esforço realizado nas tarefas pela interface WEB em português. Gestores e administradores mantêm apontamentos manuais e corrigem registros; o responsável acompanha o próprio trabalho pelo cronômetro integrado às ações da tarefa. Horas registradas alimentam os totais de tarefas, projetos e consultas.

## Resultado esperado

A pessoa inicia sua tarefa, acompanha uma única contagem e salva as horas ao pausar ou finalizar. Cada pausa encerra a execução e permite trabalhar em outra tarefa; um novo início abre outra execução de até oito horas. Gestores e administradores registram ou corrigem esforço de participantes, e os usuários consultam os apontamentos permitidos e seus totais.

## Atores e permissões

Todas as operações exigem conta ativa. Aplicar as permissões atuais inclusive em acessos diretos ou telas já abertas.

| Operação | Quem pode executar | Limites |
| --- | --- | --- |
| Consultar apontamentos e totais | Participantes nos projetos acessíveis; administradores em qualquer projeto | Inclui consulta de tarefas canceladas/arquivadas e projetos arquivados |
| Criar apontamento manual | Gestores do projeto e administradores | Pessoa selecionada deve ser participante atual e ativa; administrador não precisa participar para lançar para outra pessoa |
| Editar ou excluir apontamento | Gestores do projeto e administradores | Pode ser de qualquer pessoa e origem; respeitar estados de somente consulta |
| Iniciar, Pausar e Finalizar tarefa/cronômetro | Somente o responsável atual | Inclusive para gestores e administradores; projeto ativo e transição válida |
| Pausa por limite ou perda de vínculo | Sistema, como consequência da regra | Salvar o tempo efetivamente contado, sem finalizar a tarefa |

Administradores podem administrar qualquer projeto sem participação, mas não controlam manualmente o cronômetro de outra pessoa. Gestores só administram apontamentos dos projetos que gerenciam. Membros não criam apontamentos manuais nem editam/excluem registros, mesmo próprios.

Tarefas finalizadas admitem lançamentos e correções. Tarefas canceladas/arquivadas e projetos arquivados permitem somente consulta de apontamentos, inclusive para administradores. A criação ou edição manual não altera a situação da tarefa.

## Histórias de usuário

1. Como responsável, quero iniciar uma tarefa com seu cronômetro para registrar meu trabalho.
2. Como responsável, quero acompanhar a tarefa e o tempo globalmente, inclusive após recarregar ou voltar ao sistema.
3. Como responsável, quero pausar e salvar minhas horas para interromper o trabalho ou iniciar outra tarefa.
4. Como responsável, quero finalizar a tarefa e registrar o tempo restante sem duplicar apontamentos.
5. Como responsável, quero que a execução pause ao atingir oito horas para limitar uma contagem esquecida.
6. Como pessoa com trabalho em andamento, quero preservar as horas quando minha atribuição, participação ou situação da conta mudar.
7. Como gestor ou administrador, quero lançar horas manuais para participantes ativos do projeto, inclusive para datas passadas.
8. Como gestor ou administrador, quero corrigir ou excluir apontamentos de qualquer pessoa dentro do meu alcance autorizado.
9. Como usuário autorizado, quero filtrar e paginar apontamentos para consultar esforço por projeto, pessoa e período.
10. Como usuário autorizado, quero ver totais atualizados em tarefas, projetos e consultas.
11. Como usuário autorizado, quero receber validação e retorno das operações sem perder a compreensão do resultado.

## Fluxo principal

**Consulta:** abrir Apontamentos com todos os projetos e pessoas acessíveis, sem restrição inicial de período. Ordenar por data mais recente, desempatar pela criação mais recente e mostrar oito registros por página. Filtrar por projeto, pessoa e período De/Até inclusivo. Apresentar o total de horas de todos os resultados filtrados, não apenas da página. Também disponibilizar os registros no contexto da tarefa e do projeto.

**Lançamento manual:** gestor do projeto ou administrador abre o formulário, escolhe tarefa e participante atual ativo, informa data, duração em horas e descrição opcional. Hoje é a data inicial; aceitar passado e impedir futuro. Aceitar somente ponto no decimal, até duas casas, valor maior que zero e até 24 horas por apontamento. Converter ao minuto mais próximo. Salvar com origem Manual, confirmar e atualizar registros e totais. Cancelar o formulário não cria apontamento.

**Correção:** gestor autorizado ou administrador abre um apontamento de qualquer pessoa, inclusive de origem Cronômetro. Pode alterar tarefa, data, duração e descrição, preservando pessoa e origem. Validar acesso e elegibilidade do destino e os limites de data/duração do formulário. Salvar corrige o registro e os totais; cancelar preserva os dados anteriores. Excluir exige confirmação e atualiza os totais somente após confirmar.

**Início:** o responsável atual aciona Iniciar em uma tarefa Pendente ou Pausada de projeto ativo. Sem outro cronômetro rodando para essa pessoa, colocar a tarefa Em andamento e começar uma execução nova. Exibir tarefa e tempo da execução globalmente. A existência de apontamentos anteriores não consome o limite dessa execução.

**Pausa:** ao Pausar, interromper a contagem, gerar o apontamento ou os apontamentos por data e deixar a tarefa Pausada. A execução termina; a pessoa pode iniciar outra tarefa sem finalizar a anterior. Iniciar novamente a tarefa pausada começa outra execução com novo limite de oito horas.

**Limite automático:** ao completar oito horas de tempo contado na execução atual, o sistema executa a pausa e o registro das horas, sem finalizar a tarefa. A regra também vale quando a página estiver fechada ou a pessoa tiver saído da conta. Não contar tempo depois do limite.

**Finalização:** ao Finalizar em situação permitida, salvar apenas o tempo da execução atual ainda não registrado e colocar a tarefa Finalizada, com data/hora conforme Gestão de Tarefa. Não exigir uma ação separada para encerrar o cronômetro. Apontamentos de pausas anteriores permanecem sem duplicação. Se não houver tempo contado, finalizar sem gerar registro zero.

**Precisão e virada de dia:** ao gerar um apontamento de cronômetro, arredondar sua duração para o próximo minuto inteiro. Quando a execução atravessar meia-noite, separar o tempo por data no horário de Brasília e gerar um apontamento para cada data com tempo contado. Pausas não contam.

**Alteração de vínculo:** quando uma operação permitida trocar o responsável, remover a pessoa do projeto ou inativar sua conta durante a contagem, o sistema pausa automaticamente e salva as horas até o instante da alteração, sem finalizar a tarefa. O registro permanece em nome de quem trabalhou, ainda que a alteração retire sua participação ou acesso.

## Fluxos alternativos e exceções

- Outro cronômetro já está rodando para a pessoa: impedir um novo início e informar a execução existente; não iniciar duas contagens.
- Pessoa deixa de ser responsável ou perde autorização: impedir ações manuais indevidas. A pausa automática decorrente da alteração preserva o tempo contado e não concede controle manual a terceiros.
- Conta inativa, projeto não autorizado, pessoa manual inativa/não participante ou destino de somente consulta: impedir a operação e informar o motivo.
- Data futura, duração zero/negativa/acima de 24 horas, vírgula ou mais de duas casas no formulário manual: recusar e permitir correção.
- Cancelar formulário ou confirmação de exclusão: preservar os registros existentes.
- Finalizar tarefa sem execução atual, ou imediatamente sem tempo contado: concluir sem apontamento novo; não duplicar os já salvos e não afetar o cronômetro de outra tarefa.
- Pausar sem duração positiva: não criar registro zero.
- Tarefa cancelada/arquivada ou projeto arquivado: permitir consulta dos apontamentos, sem criar, corrigir ou excluir.
- Tentativa de arquivar projeto com cronômetro rodando: impedir e informar o motivo. Pausar já registra e encerra a execução; tarefa pausada não mantém esse impedimento.
- Recarga, fechamento da página ou saída da conta: manter a contagem correta até a pausa/finalização ou limite. Voltar ao sistema mostra a situação atual.
- Nenhum registro ou filtro sem correspondência: apresentar estado vazio e total zero. Carregamento, erro e sucesso devem ser distinguíveis; falha permite nova tentativa, sem indicar sucesso nem duplicar a operação já concluída.

## Regras de negócio

R1. Consulta segue participação ou acesso administrativo. Lançamento manual, edição e exclusão são exclusivos de gestores nos projetos gerenciados e administradores em qualquer projeto, inclusive para registros de outras pessoas.

R2. Apontamento pertence a uma tarefa, uma pessoa e uma data, com duração positiva, descrição opcional e origem Manual ou Cronômetro. Lançamento manual seleciona apenas participante atual e ativo, mesmo para data passada; não exige que seja responsável pela tarefa.

R3. Formulário manual usa hoje como padrão, aceita datas passadas e impede futuras. Duração em horas com ponto, até duas casas, maior que zero e até 24 por registro; converter ao minuto mais próximo. 1.50 representa 1h30min; 0.01 representa 1 minuto após conversão. O limite de seis horas da estimativa não limita horas realizadas.

R4. Edição pode mudar tarefa, data, duração e descrição, mas mantém pessoa e origem. O destino precisa estar no alcance de gestão e admitir o registro para a pessoa preservada. Excluir exige confirmação. Correções e exclusões atualizam todos os totais que consomem o registro.

R5. Finalizadas admitem registros e correções. Canceladas/arquivadas e projetos arquivados impedem mutações de apontamentos para todos, inclusive administradores, preservando consulta. Apontar horas manualmente não muda a situação da tarefa.

R6. Somente o responsável atual pode Iniciar/Pausar/Finalizar tarefa e cronômetro, mesmo quando gestor ou administrador. Aplicar as transições da Gestão de Tarefa. Sem responsável válido, essas ações não são permitidas.

R7. No máximo um cronômetro rodando por pessoa. Iniciar abre nova execução; Pausar salva, encerra essa execução e deixa a tarefa Pausada. Pode iniciar outra tarefa sem finalizar a anterior. Não existe Descartar.

R8. Cada execução conta até oito horas; atingido o limite, pausar e salvar automaticamente. Apontamentos anteriores não consomem o limite. Novo início após pausa abre outra execução com novo limite.

R9. Finalizar salva somente tempo ainda não registrado e finaliza a tarefa. Sem tempo contado, não cria apontamento. Não duplicar registros de pausas anteriores nem exigir encerramento separado antes de Finalizar.

R10. Cronômetro persiste após recarga, fechamento da página e saída da conta, respeitando pausa automática. A exibição global identifica tarefa e tempo da execução atual.

R11. Cronômetro arredonda cada apontamento ao próximo minuto inteiro: 1 segundo resulta em 1 minuto; 1min01s em 2 minutos. Uma execução que atravesse meia-noite é dividida por data de Brasília, contabilizando somente o tempo trabalhado em cada data.

R12. Troca permitida de responsável, remoção de participante ou inativação durante a contagem pausa e registra até o instante da alteração, sem finalizar tarefa. Não transferir as horas para novo responsável ou para quem executou a alteração.

R13. Apontamentos permite filtros por projeto, pessoa e período De/Até inclusivo. Inicialmente sem limite de período e com todo o conjunto acessível. Ordenar por data decrescente e, em empate, criação decrescente; oito registros por página. Total considera todos os resultados filtrados.

R14. Horas realizadas em tarefa e projeto são a soma dos respectivos apontamentos, refletindo criação, edição e exclusão. Consulta de histórico preserva registros de tarefas/projetos de somente consulta. Tempo apenas em contagem ainda não é apontamento salvo.

R15. Arquivar projeto é impedido enquanto houver cronômetro rodando nele. Preservar transições válidas das tarefas: não permitir Cancelar/Arquivar diretamente uma tarefa Em andamento. A pausa salva e remove a execução aberta, sem criar exceção às demais permissões.

## Dados percebidos pelo usuário

Tarefa e projeto, pessoa, data, duração, descrição opcional, origem Manual/Cronômetro; formulário de criação/correção, confirmação de exclusão, filtros de projeto/pessoa/período, lista paginada e total filtrado. Cronômetro global com tarefa, tempo da execução e ações permitidas; situação da tarefa e horas realizadas em seus contextos. Tabela e cards no mobile, com carregamento, vazio, erro, indisponibilidade e sucesso.

## Critérios de aceite

CA1 — Como gestor, ao lançar/corrigir horas, permitir somente projetos gerenciados. Como administrador ativo, permitir qualquer projeto mesmo sem participação. Como membro, recusar criação manual, edição e exclusão, inclusive de registro próprio. [R1]

CA2 — Ao criar manualmente, permitir participante atual ativo, inclusive outra pessoa e sem exigir responsabilidade pela tarefa; recusar pessoa inativa ou que deixou o projeto mesmo para data passada. Preservar origem Manual. [R2]

CA3 — Ao abrir formulário manual, sugerir hoje. Aceitar ontem; recusar data futura. Aceitar 1.50 como 1h30 e 24; recusar zero, negativo, acima de 24, vírgula ou mais de duas casas. Converter 0.01 para 1 minuto. [R3]

CA4 — Como gestor autorizado ou administrador, ao corrigir apontamento alheio Manual ou Cronômetro, permitir tarefa/data/duração/descrição e preservar pessoa/origem. Destino sem acesso ou que não admite o registro é recusado. Cancelar mantém o original. [R4]

CA5 — Ao excluir apontamento autorizado, pedir confirmação; confirmar remove e atualiza totais, cancelar preserva. Pessoa sem permissão não pode excluir. [R1, R4]

CA6 — Em tarefa finalizada de projeto ativo, permitir lançamentos/correções autorizados sem mudar situação. Em cancelada, arquivada ou projeto arquivado, impedir mutações inclusive pelo administrador e manter consulta. [R5]

CA7 — Como responsável atual em tarefa Pendente ou Pausada de projeto ativo, ao Iniciar sem outro cronômetro rodando, colocar Em andamento e iniciar contagem. Gestor ou administrador não responsável é impedido; ninguém controla manualmente o cronômetro alheio. [R6–R7]

CA8 — Com cronômetro em A, ao tentar Iniciar B, recusar sem iniciar segunda contagem. Após Pausar A, salvar suas horas, deixar A Pausada e permitir Iniciar B sem finalizar A. [R7]

CA9 — Após pausar uma tarefa com horas registradas, ao Iniciar novamente, começar nova execução e novo limite de oito horas, sem consumir o limite pelos registros anteriores. [R7–R8]

CA10 — Com execução atual atingindo oito horas, mesmo após logout ou fechamento da página, pausar automaticamente, salvar somente até o limite e deixar a tarefa Pausada. [R8, R10]

CA11 — Ao Finalizar com contagem, registrar somente o tempo atual ainda não salvo e tornar a tarefa Finalizada com data/hora. Registros de pausas anteriores não são duplicados. Sem tempo contado, finalizar sem apontamento novo. Não exigir encerramento separado. [R9]

CA12 — Ao recarregar, fechar/reabrir a página ou sair/entrar na conta durante contagem, apresentar tarefa e tempo atuais, incluindo eventual pausa automática nas oito horas. Não contar o intervalo após uma pausa. [R8, R10]

CA13 — Ao gerar apontamento de 1 segundo, registrar 1 minuto; de 1min01s, registrar 2 minutos. Duração zero não produz apontamento. [R9, R11]

CA14 — Com execução entre 23h50 e 00h10 de Brasília, ao pausar ou finalizar, gerar 10 minutos na primeira data e 10 na segunda, em nome da mesma pessoa. [R11]

CA15 — Com contagem rodando, ao efetivar troca autorizada de responsável, remoção de participante ou inativação, pausar e salvar até aquele instante em nome de quem trabalhou; não finalizar a tarefa nem continuar contando. [R12]

CA16 — Ao abrir Apontamentos sem filtros, mostrar todos os registros acessíveis, sem período inicial, por data mais recente e criação mais recente nos empates. Pessoa sem acesso não vê registros restritos; administrador consulta todos os projetos. [R1, R13]

CA17 — Ao filtrar por projeto, pessoa e período, apresentar somente correspondências e incluir registros nas datas De e Até. Com mais de oito resultados, paginar em oito e manter o total de todos os resultados filtrados. Sem correspondências, mostrar vazio e zero. [R13]

CA18 — Após criar, corrigir duração, mudar tarefa ou excluir apontamento autorizado, ao consultar totais de tarefa/projeto e consulta filtrada, refletir a soma dos registros correspondentes; não incluir tempo ainda não salvo. [R4, R14]

CA19 — Com cronômetro rodando no projeto, ao tentar arquivar, impedir e explicar. Após a pausa, não manter impedimento por essa execução já encerrada, respeitando as demais condições de arquivamento. [R15]

CA20 — Com tarefa Em andamento, ao tentar Cancelar/Arquivar diretamente, recusar. Após Pausar, aplicar as ações permitidas da Gestão de Tarefa. [R6, R15]

CA21 — Em falha de operação, mostrar erro e permitir nova tentativa, sem anunciar sucesso nem duplicar apontamento já salvo. Cancelar formulário ou exclusão preserva os registros. [Fluxos alternativos]

CA22 — Em desktop/mobile, ao usar formulário, filtros, tabela/cards e cronômetro, manter dados e ações essenciais acessíveis por teclado, com labels, foco e mensagens. Distinguir carregamento, vazio, erro e sucesso. [Dados percebidos; guia]

## Dependências

Gestão de Tarefa (#1014454), com relação nativa 666 já criada e conferida: #1014454 bloqueia #1014493. Fornece tarefa, situação, responsabilidade e transições. Projetos, participantes, papéis e situação da conta vêm das capacidades anteriores por essa cadeia.

Gestão de Tempo entrega os apontamentos, totais e integração do cronômetro consumidos por Minhas Tarefas, Quadro do Projeto, Painel Gerencial e detalhes/listas de tarefas e projetos. A integração acrescenta o bloqueio de arquivamento por contagem em andamento e o salvamento por perda de vínculo, sem criar dependência reversa de criação de tarefa.

## Designs e evidências

- [Guia de design](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md), [Apontamentos](../../scopes/2026-09-09-nexum-scope/sources/design-time-entries.md), [Detalhes da tarefa](../../scopes/2026-09-09-nexum-scope/sources/design-task-detail.md) e [Minhas Tarefas](../../scopes/2026-09-09-nexum-scope/sources/design-my-tasks.md).
- [Entrevista](interview.md): Q70–Q95 e confirmação explícita do entendimento por Mário Tinelli.
- [Catálogo completo revisado aprovado](../../scopes/2026-09-09-nexum-scope/catalog-time-review.md), aprovação catalog-time-review-001.
- As respostas substituem nas referências a edição exclusiva de apontamentos próprios, duração manual em minutos, Descartar, execução aberta durante pausa e data única de encerramento. Cada pausa salva e fecha execução; novo início abre outra de até oito horas. O acesso administrativo amplo preserva as exceções de cronômetro próprio, responsável e somente consulta.

## Dentro do escopo

Apontamentos manuais, correção e exclusão autorizadas, cronômetro global persistente integrado às ações de tarefa, pausa automática e por perda de vínculo, precisão e divisão por data, consulta filtrada/paginada, registros contextuais e totais. Interface WEB em português, responsiva, com formulários, confirmações, tabela/cards e estados de retorno. Aplicam-se os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento.

## Fora do escopo

Aprovação de horas, faturamento, centros de custo, importação/sincronização externa, controle manual de cronômetro alheio, Descartar, aplicativo nativo, API pública e escolhas de implementação. Minhas Tarefas, Quadro e Painel mantêm suas entregas próprias; Gestão de Tempo fornece as regras e dados que consomem.

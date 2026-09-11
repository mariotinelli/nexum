# Entrevista — Gestão de Tempo (#1014493)

## Evidências e árvore inicial

Fontes compartilhadas design-guide, design-time-entries, design-task-detail e design-my-tasks. Relação nativa 666 confirmada: Gestão de Tarefa (#1014454) bloqueia Gestão de Tempo; status New preservado. Catálogo aprovado e dados/fluxo de tarefa já definidos. Leitura estática das funções startTimer, elapsed e entryModal de apontamentos.html e seções F09/F10/RN06–RN09/RN14 do guia, sem executar conteúdo do protótipo.

Evidências: cronômetro global identifica tarefa e tempo; uma execução aberta por pessoa, inclusive pausada; pausas não contam; contagem sobrevive a recarregar/fechar página. Encerrar gera apontamento, descartar exige confirmação. Apontamento tem tarefa, pessoa, data, duração positiva, descrição opcional e origem. Protótipo usa minutos manuais, arredonda cronômetro para cima e usa data do encerramento; permite editar tarefa/data/duração/descrição, preservando pessoa e origem. Essas propostas precisam de confirmação quando constituem escolhas do produto.

Regras herdadas: somente o responsável atual pode Iniciar/Pausar/Finalizar tarefa, inclusive gestor apenas se também responsável. Gestores criam/editam dados, Cancelam/Arquivam/Desarquivam conforme situações; não ampliar poderes nesta entrevista sem revisão explícita. Gestão de Tempo integra cronômetro e ações; finalizar/descartar execução aberta precede Finalizar/Arquivar tarefa quando permitido e arquivar projeto. Canceladas/arquivadas e projetos arquivados permitem consulta, sem mutações. Editar/excluir apontamentos somente próprios; acesso por participação, sem privilégio automático do administrador. Realizadas são soma de apontamentos, sem aprovação/faturamento/centro de custo. Limite de seis horas é da estimativa da tarefa, sem autorização para copiá-lo para esforço real.

Árvore: integração entre ações e cronômetro; autorização e dados do lançamento manual; correção; consulta; precisão e virada de dia. Fronteira Q70–Q77. Descendentes aguardam integração: efeito de Encerrar/Descartar sobre situação, perda de atribuição/participação ou conta inativa com execução aberta, saída da conta e resolução de cronômetro que ficou sem autorização. Limites diários e tratamento de vários registros dependem das decisões de duração/virada de dia. Nenhuma escolha de biblioteca, persistência ou implementação será perguntada.

## Q70 — Iniciar e Pausar

Depois da integração, Iniciar tarefa deve também iniciar seu cronômetro, e Pausar tarefa deve pausar ambos?

Recomendação: sim, mantendo essas ações exclusivas do responsável atual e a regra de uma execução aberta por pessoa. O efeito de encerrar ou descartar a execução sobre a situação será tratado após esta decisão.

Estado: blocking. Resposta: aguardando.

## Q71 — Quem lança horas manualmente

Qualquer participante ativo pode registrar horas próprias em uma tarefa acessível, mesmo sem ser seu responsável, inclusive em tarefa Finalizada?

Recomendação: sim, permitindo registrar colaboração. Pessoa é automática; ninguém lança em nome de outra pessoa. Tarefas Canceladas/Arquivadas e projetos arquivados continuam sem alterações.

Estado: blocking. Resposta: aguardando.

## Q72 — Duração manual

Podemos receber horas decimais com até duas casas, aceitando ponto ou vírgula, maiores que zero e até 24 horas por apontamento?

Recomendação: sim, convertendo ao minuto mais próximo: 1,5 → 1h30min. O limite de seis horas continua exclusivo da estimativa; o teto de 24 horas considera que o apontamento manual representa uma data.

Estado: blocking. Resposta: aguardando.

## Q73 — Data do lançamento manual

Usar hoje como padrão e permitir datas passadas, mas impedir datas futuras?

Recomendação: sim, pois o apontamento representa esforço já realizado.

Estado: blocking. Resposta: aguardando.

## Q74 — Correção de apontamentos

Ao editar um apontamento próprio, permitir alterar tarefa, data, duração e descrição, mantendo pessoa e origem Manual/Cronômetro originais?

Recomendação: sim, inclusive para corrigir registros produzidos pelo cronômetro. A tarefa de destino deve estar acessível e permitir lançamentos; excluir continua exigindo confirmação.

Estado: blocking. Resposta: aguardando.

## Q75 — Consulta inicial

Abrir com todos os projetos e pessoas acessíveis, sem limite de período, ordenando por data mais recente, com oito registros por página e total de horas de todos os resultados filtrados?

Recomendação: sim, seguindo os filtros da referência e a paginação já adotada. De/Até são inclusivos; o total não se limita à página atual. Em empate de data, usar criação mais recente.

Estado: blocking. Resposta: aguardando.

## Q76 — Arredondamento do cronômetro

Ao gerar um apontamento, arredondar o tempo contado para o próximo minuto inteiro?

Recomendação: sim, como na referência: 1 segundo → 1 minuto; 1min01s → 2 minutos. Pausas não contam; duração zero não gera apontamento válido e a execução pode ser descartada.

Estado: blocking. Resposta: aguardando.

## Q77 — Execução atravessando a meia-noite

Se uma execução atravessar a meia-noite, dividir o tempo contado em um apontamento para cada data, usando o horário de Brasília?

Recomendação: sim, para atribuir o esforço ao dia em que ocorreu, sem contabilizar pausas. Isso substitui a data única do encerramento usada pelo protótipo.

Estado: blocking. Resposta: aguardando.

## Respostas Q70–Q77 — 2026-09-10T16:11:40.666359Z

Proveniência: Mário Tinelli, nesta conversa.

### Q70

Resposta literal: sim

Decisão: Iniciar tarefa também inicia seu cronômetro; Pausar pausa tarefa e cronômetro. Ações exclusivas do responsável atual, com uma execução aberta por pessoa.

### Q71

Resposta literal: nao, apenas gestor e admin pode lançar horas manuais

Decisão: Lançamento manual exclusivo de gestores e administradores. Definir alcance por projeto e lançamento em nome de outra pessoa.

### Q72

Resposta literal: sim, mas com ponto em vez de virgula

Decisão: Duração manual em horas decimais até duas casas, somente ponto como separador, maior que zero e até 24 horas por apontamento; converter ao minuto mais próximo. Limite de seis horas exclusivo da estimativa.

### Q73

Resposta literal: sim

Decisão: Data manual padrão hoje; aceitar datas passadas e impedir futuras.

### Q74

Resposta literal: apenas gestou e admins

Decisão: Edição de apontamentos exclusiva de gestores e administradores; esclarecer alcance sobre registros alheios e exclusão. Campos e origem seguem a proposta de Q74, sujeita ao alcance confirmado.

### Q76

Resposta literal: sim

Decisão: Cronômetro arredonda para o próximo minuto inteiro ao gerar apontamento; pausas não contam; duração zero não gera apontamento válido.

### Q77

Resposta literal: sim

Decisão: Execução que atravessa meia-noite é dividida em um apontamento por data no horário de Brasília, contando somente tempo ativo.

### Q75 — Pedido de esclarecimento

Resposta literal: o que é essa consulta ?

Esclarecimento: é a tela de Apontamentos, que lista horas registradas nas tarefas com filtros por projeto, pessoa e período e total de horas. Nenhuma aprovação dos padrões foi presumida; Q75 permanece blocking.

Q71/Q74 substituem permissões anteriores e têm descendentes. Q72 confirma somente ponto, recusando vírgula; Q73/Q76/Q77 resolvidas. Pausa de avanço para revisão do catálogo preserva issues, operações e aprovações anteriores. Ainda é possível esclarecer perguntas independentes da entrevista.

## Fronteira após Q70–Q77

### Q75 — Tela de Apontamentos, esclarecida

Nessa tela que lista as horas registradas, podemos manter todos os projetos e pessoas acessíveis, sem limite inicial de período, data mais recente primeiro, oito registros por página e total de todos os resultados filtrados?

Recomendação: sim. De/Até são inclusivos e empate de data usa criação mais recente; o total não se restringe à página atual.

Estado: blocking. Resposta: aguardando.

### Q78 — Lançar em nome de outra pessoa

Gestores e administradores podem lançar horas manuais em nome de outro participante, além de si mesmos?

Recomendação: sim, para que consigam registrar ou corrigir horas que um membro deixou de apontar; a pessoa fica explicitamente identificada no lançamento.

Estado: blocking. Resposta: aguardando.

### Q79 — Editar registros de outras pessoas

Gestores e administradores podem editar apontamentos de qualquer pessoa nos projetos em que têm autorização, mantendo pessoa e origem originais?

Recomendação: sim, pois a correção passou a ser uma responsabilidade desses perfis. Continuam editáveis tarefa, data, duração e descrição, respeitando o acesso e o estado da tarefa/projeto.

Estado: blocking. Resposta: aguardando.

### Q80 — Quem pode excluir

A exclusão de apontamentos também deve ser exclusiva de gestores e administradores?

Recomendação: sim, mantendo confirmação antes de excluir e alinhando a exclusão à permissão de correção. A resposta Q74 foi tratada como restrição de edição, sem presumir a exclusão.

Estado: blocking. Resposta: aguardando.

### Q81 — Alcance por projeto

Gestores operam horas somente nos projetos que gerenciam, e administradores precisam participar do projeto para lançar, editar ou excluir horas?

Recomendação: sim, preservando a regra já aprovada de que administração não concede acesso automático aos projetos. Um administrador participante pode usar essas funções mesmo sem papel Gestor.

Estado: blocking. Resposta: aguardando.

### Q82 — Encerrar ou descartar o cronômetro

Encerrar o cronômetro deve registrar as horas e deixar a tarefa Pausada; descartar deve deixar a tarefa Pausada sem registrar horas, mantendo Finalizar tarefa como uma ação separada?

Recomendação: sim. Assim, encerrar uma sessão de trabalho não finaliza a tarefa. Finalizar tarefa continua exigindo encerrar ou descartar a execução aberta antes; não cria horas novamente.

Estado: blocking. Resposta: aguardando.

### Q83 — Sair da conta

Ao sair da conta, o cronômetro deve continuar contando, como já ocorre ao fechar a página?

Recomendação: sim, preservando a execução até a pessoa pausar, encerrar ou descartar. Ao entrar novamente, ela encontra a execução aberta; se já estava pausada, permanece pausada.

Estado: blocking. Resposta: aguardando.

Descendentes ainda retidos: efeito de perda de atribuição/participação ou inativação durante execução depende de Q82; alcance de exclusão sobre registros alheios depende de Q79/Q80; seleção de pessoa no lançamento manual depende de Q78/Q81. Sem decisão adiada por vontade do usuário nem pergunta técnica.

## Respostas Q75 e Q78–Q83 — 2026-09-10T16:16:03.454719Z

Proveniência: Mário Tinelli, nesta conversa.

### Q75

Resposta literal: sim

Decisão: Consulta de Apontamentos com todos os projetos/pessoas acessíveis, sem período inicial, data mais recente, oito por página, total de todos os resultados filtrados; De/Até inclusivos e desempate pela criação mais recente.

### Q78

Resposta literal: sim

Decisão: Gestores e administradores podem lançar horas manuais para outro participante, além de si mesmos.

### Q79

Resposta literal: sim

Decisão: Gestores e administradores podem editar apontamentos de qualquer pessoa nos projetos autorizados, mantendo pessoa/origem e corrigindo tarefa/data/duração/descrição.

### Q80

Resposta literal: sim

Decisão: Exclusão exclusiva de gestores e administradores, com confirmação; alcance sobre registros de qualquer pessoa segue a correção confirmada em Q79.

### Q81

Resposta literal: Gestores operam somente nos projetos que gerenciam, administradores podem fazer o que quiser em qualquer projeto

Decisão: Gestores operam nos projetos que gerenciam; administradores podem operar em qualquer projeto. Esclarecer alcance dessa exceção entre capacidades e estados de somente consulta.

### Q82

Resposta literal: não existe descartar, apenasa opção de pausar ou finalizar

Decisão: Remover Descartar; controles de encerramento são Pausar ou Finalizar. Efeito de Finalizar o cronômetro sobre a situação da tarefa ainda não confirmado.

### Q83

Resposta literal: continua, mas existe um limite, se bater 8 horas pausa sozinho

Decisão: Cronômetro continua após sair da conta, com pausa automática ao atingir oito horas. Definir unidade de aplicação do limite e efeitos da pausa.

Q81 contradiz o limite anterior de participação para administradores; alcance funcional ainda pendente. Q82 retira Descartar, substituindo catálogo/guia e exigindo reconciliação dos bloqueios que mencionavam essa opção; não foi aceita implicitamente a sugestão de deixar a tarefa Pausada ao finalizar o cronômetro. Q83 limita a contagem anteriormente contínua. A pausa vigente para revisão do catálogo permanece, sem mutações remotas ou mudanças no catálogo aprovado.

## Q84 — Alcance da exceção administrativa

Podemos limitar o acesso administrativo a qualquer projeto às funções de Gestão de Tempo, mantendo as permissões já aprovadas de Gestão de Projeto e Gestão de Tarefa?

Recomendação: sim, pois a decisão surgiu na administração dos apontamentos. Uma alteração global dessas outras capacidades precisa ser explicitada antes de reconciliar seus requisitos.

Estado: blocking. Resposta: aguardando.

## Q85 — Contagem do limite de oito horas

O limite vale para cada execução do cronômetro, somando seus períodos ativos e descontando as pausas?

Recomendação: sim. Assim, oito horas significam oito horas efetivamente contadas na mesma execução, mesmo que ela tenha sido pausada ou atravesse dias. O efeito de tentar continuar após atingir o limite será definido depois.

Estado: resolved. Resposta e decisão atribuídas abaixo.

## Q86 — Finalizar cronômetro e tarefa

Finalizar o cronômetro deve registrar as horas e também deixar a tarefa Finalizada?

Recomendação: sim, alinhando esse controle à ação Finalizar da tarefa; Pausar conserva o trabalho para continuar depois. Essa proposta precisa da confirmação do usuário, pois Q82 não definiu o efeito sobre a tarefa.

Estado: resolved. Resposta e decisão atribuídas abaixo.

Descendentes retidos: limites do administrador em estados de somente consulta dependem de Q84; continuidade ao atingir oito horas depende de Q85; perda de atribuição/participação, inativação e execução com tempo zero dependem do encerramento sem Descartar definido em Q86. Seleção de pessoa em lançamento manual permanece ramo a auditar após alcance administrativo. Pausa vigente continua sendo gate de catálogo, não adiamento do usuário.

## Respostas Q84–86 — Mário Tinelli

Q84: “nao entendi”. Continua blocking, sem confirmação do alcance administrativo.

Q85: “se eu entend, sim é dessa forma, não importante os apontamentos uqe ja fora criados, esse limite de 8 horas é da execução atual”. Resolvido: limite apenas da execução atual, períodos ativos acumulados e pausas descontadas; apontamentos já criados não consomem o limite.

Q86: “sim”. Resolvido: finalizar cronômetro registra horas e finaliza a tarefa.

## Fronteira seguinte

### Q84 — Reformulação: poderes do administrador

Quando você diz que o administrador pode fazer qualquer coisa em qualquer projeto, isso inclui editar e arquivar projetos e tarefas, mesmo sem participar deles?

Recomendação: sim, seguindo a expressão usada em Q81. Isso revisa a regra anterior que exigia participação; a extensão continua pendente de resposta explícita.

Estado: resolved. Resposta atribuída abaixo.

### Q87 — Continuar após oito horas

Se o cronômetro pausar automaticamente nas oito horas e a tarefa ainda não estiver pronta, como a pessoa deve continuar trabalhando nela?

Sem recomendação fechada: precisamos conciliar o limite por execução com a retomada do trabalho, pois Finalizar também conclui a tarefa e não existe Descartar. A resposta definirá o encerramento da execução e o momento de gerar seus apontamentos nesse caso.

Estado: blocking quanto à retomada. Pausar e contabilizar sem concluir a tarefa foi confirmado; esclarecimento em Q89.

### Q88 — Finalização sem tempo contado

Se a pessoa iniciar e finalizar imediatamente, sem nenhum tempo contado, podemos finalizar a tarefa sem criar apontamento?

Recomendação: sim, para permitir a conclusão sem gerar um registro de duração zero.

Estado: resolved. Resposta atribuída abaixo.

Descendentes retidos: tratamento da execução ao trocar responsável, remover participação ou inativar pessoa depende de Q87 (fechamento de execução sem concluir tarefa) e Q84 (poderes administrativos). Elegibilidade da pessoa selecionada em lançamento manual e exceções em projetos/tarefas de somente consulta dependem de Q84. Nenhuma aprovação de catálogo nem publicação foi inferida.

## Respostas Q84, Q87 e Q88 — Mário Tinelli

Q84: “sim”. Resolvido: administrador pode atuar em qualquer projeto, inclusive editar e arquivar projetos e tarefas sem participar. Essa decisão alcança capacidades anteriores e exige reconciliar o catálogo e identificar requisitos afetados antes de propor suas atualizações; não autoriza publicação remota automática.

Q87: “apenas pausa e contabiliza o tempo”. Confirmado: nas oito horas, pausar e contabilizar sem finalizar tarefa. “Contabiliza” não esclarece por si só se já cria apontamento, se isso vale também para pausa manual nem como reinicia o limite ao retomar. Esses efeitos permanecem blocking em Q89.

Q88: “sim”. Resolvido: finalizar tarefa sem apontamento quando não houver tempo contado.

## Nova fronteira

### Q89 — Apontamento na pausa e retomada

Ao pausar, manualmente ou pelo limite de oito horas, o sistema já deve salvar um apontamento; ao retomar, começa outra execução com um novo limite de oito horas?

Recomendação: sim. Assim, as horas ficam registradas a cada pausa e a pessoa consegue continuar a tarefa sem finalizá-la. Isso substituiria a interpretação anterior de uma mesma execução atravessar pausas; depende de confirmação explícita.

Estado: resolved. Resposta atribuída abaixo.

### Q90 — Administrador e registros de somente consulta

Mesmo para administradores, tarefas canceladas ou arquivadas e projetos arquivados devem impedir alterações nos apontamentos?

Recomendação: sim, preservando o histórico; acesso a qualquer projeto não precisa remover essa proteção.

Estado: resolved. Resposta atribuída abaixo.

### Q91 — Pessoa no lançamento manual

No lançamento manual, só podem ser selecionadas pessoas ativas que ainda participam do projeto, mesmo quando o lançamento se refere a uma data passada?

Recomendação: sim, para seguir a participação atual. Caso seja necessário corrigir horas de ex-participantes, essa exceção precisa ser definida.

Estado: resolved. Resposta atribuída abaixo.

### Q92 — Administrador e cronômetros de outras pessoas

O administrador também pode pausar e finalizar o cronômetro de outra pessoa, mantendo as horas em nome dela?

Recomendação: sim, para permitir resolver uma execução que ficou aberta sem atribuir o tempo ao administrador.

Estado: resolved. Resposta atribuída abaixo.

Descendentes retidos: troca de responsável, remoção de participante e inativação dependem de Q89 e Q92 para definir o destino da execução e das horas. Seleção de ex-participante/inativo depende de Q91. Exceções em estados de somente consulta dependem de Q90. Catálogo aprovado permanece intacto, com gate de revisão vigente; nenhum requisito anterior foi alterado nem publicado.

## Respostas Q89–92 — Mário Tinelli

Q89: “sim”. Cada pausa manual ou automática salva um apontamento; retomar inicia nova execução e novo limite de oito horas. Essa resposta substitui explicitamente a interpretação anterior de Q85 em que pausas mantinham a mesma execução. Apontamentos anteriores continuam sem consumir o limite. A geração do apontamento respeita tempo positivo, arredondamento e divisão por data já decididos. Q87 fica resolvida por este esclarecimento.

Q90: “sim”. Estados de somente consulta impedem alterações nos apontamentos inclusive pelo administrador.

Q91: “sim”. Seleção manual limitada a participantes atuais e ativos, inclusive para data passada.

Q92: “não”. Administrador não pode pausar nem finalizar cronômetro de outra pessoa. Não ampliar essa resposta para impedir edição administrativa de apontamentos já permitida; controle do cronômetro e edição de registros são ações distintas.

## Nova fronteira

### Q93 — Alternar tarefas após uma pausa

Depois de pausar a tarefa A e salvar suas horas, a pessoa pode iniciar a tarefa B sem finalizar A?

Recomendação: sim, permitindo alternar tarefas e mantendo somente um cronômetro rodando por pessoa. Isso substituiria a restrição anterior de uma tarefa pausada ainda impedir outra execução.

Estado: resolved. Resposta atribuída abaixo.

### Q94 — Perda da condição de responsável ativo

Se houver troca de responsável, remoção da pessoa do projeto ou inativação da conta enquanto seu cronômetro estiver rodando, o sistema deve pausá-lo automaticamente e salvar as horas até aquele instante, sem finalizar a tarefa?

Recomendação: sim, preservando o tempo trabalhado e evitando que o cronômetro continue depois da perda da autorização. Aplicar quando a alteração de responsável, participação ou conta for permitida pelas regras correspondentes; não criar novas permissões para essas alterações. Trata-se de efeito automático, não de controle manual por administrador sobre outro cronômetro.

Estado: resolved. Resposta atribuída abaixo.

Descendentes retidos: efeitos da pausa sobre liberação da execução e bloqueios de arquivamento dependem de Q93; efeitos da perda de vínculo dependem de Q94. Depois dessas respostas, auditar integrações com Finalizar/Arquivar/Cancelar e substituição de responsável nas capacidades anteriores, preservando os gates de revisão do catálogo e aprovação das projeções. Nenhuma mutação remota realizada.

## Respostas Q93–94 — Mário Tinelli

Q93: “sim”. Pode pausar A, salvar as horas e iniciar B sem finalizar A. Somente um cronômetro rodando por pessoa. Uma tarefa pausada não mantém execução aberta nem impede outra execução.

Q94: “sim”. Troca de responsável, remoção do projeto ou inativação da conta, quando permitidas pelas respectivas capacidades, pausam automaticamente o cronômetro em andamento, salvam as horas até o instante da alteração e não finalizam a tarefa.

## Auditoria de integração após Q94

Releitura de Gestão de Tarefa e Gestão de Projeto: o arquivamento de projeto é impedido enquanto houver cronômetro aberto; isso permanece aplicável a cronômetro rodando, pois pausar agora salva e encerra a execução. Cancelar/Arquivar tarefa Em andamento não são transições permitidas. Em tarefa Pausada, o tempo já foi salvo; não exigir Descartar, que foi removido. Finalizar deve integrar o salvamento do tempo e a conclusão, sem o antigo pré-requisito circular de finalizar o cronômetro antes de Finalizar tarefa. Finalizar tarefa sem contagem atual não gera novo apontamento nem duplica registros de pausas anteriores. Estados de somente consulta e transições válidas continuam aplicáveis.

Q84 amplia a administração de projetos/tarefas sem participação, enquanto Q70 reserva Iniciar/Pausar/Finalizar ao responsável e Q92 veda controlar cronômetro alheio. A precedência para as ações da tarefa ainda precisa ser expressamente reconciliada em Q95, evitando ampliar ou restringir silenciosamente o administrador.

Impactos a reconciliar no catálogo e nos requisitos anteriores: Gestão de Projeto, Gestão de Tarefa e suas consultas deixam de exigir participação do administrador para o acesso amplo confirmado. Gestão de Tempo substitui permissões de apontamentos próprios, Descartar, execução persistente durante pausa e bloqueios correspondentes. Preservar issues, relações, ordem e fontes; preparar prévias e aprovações conforme o fluxo, sem reescrever projeções existentes automaticamente.

### Q95 — Ações da tarefa reservadas ao responsável

Mesmo podendo administrar qualquer projeto, o administrador só pode Iniciar, Pausar e Finalizar uma tarefa quando ele próprio for o responsável?

Recomendação: sim, mantendo a regra já definida para essas três ações e a proibição de controlar o cronômetro de outra pessoa. Ele continua podendo editar dados, atribuir responsáveis e executar as demais ações administrativas permitidas.

Estado: resolved. Resposta atribuída abaixo.

Próximo passo após Q95: auditar a precedência confirmada, consolidar o entendimento funcional para confirmação explícita e preparar a revisão completa do catálogo e o tratamento das projeções anteriores afetadas. Não presumir confirmação do entendimento pela resposta à última pergunta.

## Resposta Q95 — Mário Tinelli

Resposta literal: “sim”.

Decisão: Iniciar, Pausar e Finalizar tarefa são exclusivos do responsável atual, inclusive para administradores. Mantidas as demais permissões administrativas, respeitando situações e demais limites.

## Auditoria funcional e entendimento para confirmação

Estado atual: Q70–Q95 resolvidas pelas respostas e esclarecimentos posteriores. As marcações blocking anteriores pertencem ao histórico dos respectivos momentos, e não representam lacunas atuais. Q85 foi parcialmente substituída por Q89; o limite continua por execução atual, porém cada pausa encerra essa execução. Descartar foi removido por Q82; permissões próprias e acesso administrativo limitado foram substituídos por Q71/Q74/Q78–Q84, com exceções Q90/Q92/Q95. Não há decisão técnica pendente convertida em requisito.

Cobertura auditada: atores/acesso; lançamentos e correções; entradas/datas/precisão; consulta e totais; início/pausa/finalização; repetição/troca de tarefa; limite de oito horas e persistência após logout; perda de vínculo; estados de somente consulta; integração com arquivamento e transições existentes; erro/vazio conforme evidência. Nenhum ramo funcional conhecido permanece sem resposta. Confirmação explícita deste entendimento ainda pendente, e gate de revisão do catálogo permanece aberto.

1. **Permissões.** Gestores administram apontamentos dos projetos que gerenciam. Administradores acessam e administram qualquer projeto, mesmo sem participar. Essa ampliação também alcança projetos, tarefas e consultas, mas Iniciar/Pausar/Finalizar tarefa continuam exclusivos do responsável atual. Ninguém recebe permissão para controlar manualmente cronômetro de outra pessoa.

2. **Lançamento manual.** Somente gestores e administradores criam apontamentos, para si ou outro participante atual e ativo do projeto. Informar tarefa, pessoa, data, duração e descrição opcional; origem Manual. Não exigir que a pessoa selecionada seja responsável pela tarefa. Data padrão hoje; passado permitido e futuro recusado. Duração em horas decimais, somente ponto, até duas casas, maior que zero e no máximo 24 horas por registro; converter ao minuto mais próximo. Exemplo: 1.50 = 1h30. A estimativa de seis horas da tarefa não limita o esforço realizado.

3. **Correção e exclusão.** Somente gestores e administradores podem editar/excluir apontamentos, inclusive alheios e de origem Cronômetro, no seu alcance autorizado. Edição altera tarefa, data, duração e descrição, preservando pessoa e origem. Destino precisa admitir o registro. Excluir exige confirmação. Tarefas finalizadas admitem registros/correções; tarefas canceladas/arquivadas e projetos arquivados impedem mutações inclusive pelo administrador.

4. **Cronômetro.** Iniciar tarefa inicia a contagem. Somente um cronômetro rodando por pessoa. A contagem persiste ao recarregar, fechar a página ou sair da conta. Exibir globalmente tarefa e tempo da execução atual.

5. **Pausa e retomada.** Toda pausa, manual ou automática, salva o tempo como apontamento de origem Cronômetro e deixa a tarefa Pausada. Pode iniciar outra tarefa sem finalizar a anterior. Retomar pelo Iniciar começa nova execução e novo limite de oito horas. Apontamentos anteriores não consomem esse limite.

6. **Limite e finalização.** Nas oito horas da execução atual, pausar automaticamente e registrar as horas. Finalizar registra o tempo ainda não salvo e finaliza a tarefa. Não duplicar apontamentos anteriores. Sem tempo contado, concluir a tarefa sem criar registro zero. Não existe Descartar.

7. **Precisão e datas.** Cronômetro arredonda para o próximo minuto inteiro ao gerar cada apontamento: 1 segundo = 1 minuto; 1min01s = 2 minutos. Execução que atravessa meia-noite gera apontamentos separados por data de Brasília, somente com tempo efetivamente contado.

8. **Mudanças de responsável ou acesso.** Troca de responsável, remoção da pessoa do projeto ou inativação da conta, quando permitidas, pausam automaticamente a contagem e salvam as horas até aquele instante, sem finalizar a tarefa.

9. **Consulta e totais.** Página de Apontamentos e registros por tarefa/projeto acessíveis, com filtros por projeto, pessoa e período inclusivo De/Até. Inicialmente sem restrição de período e com todos os projetos/pessoas acessíveis. Ordenar por data mais recente, desempatar pela criação mais recente e paginar em oito registros. Total considera todos os resultados filtrados, não só a página. Horas realizadas das tarefas/projetos somam os apontamentos; correções e exclusões atualizam esses totais.

10. **Integrações e limites.** Arquivar projeto continua bloqueado enquanto existir cronômetro rodando nele. Preservar transições válidas da tarefa; a pausa já registra e encerra a execução, removendo bloqueios derivados de execução pausada. Gestão de Tempo não inclui aprovação de horas, faturamento, centros de custo ou integração externa.

Confirmação do entendimento: aguardando resposta explícita de Mário Tinelli. Esta confirmação não equivale à aprovação do catálogo revisado, do documento final ou de publicação remota. Próximo passo após confirmar: revisão completa do catálogo com impactos das permissões administrativas e das novas regras de execução, preservando issues e relações existentes.

## Confirmação explícita do entendimento

Mário Tinelli respondeu “confirmo” ao entendimento consolidado apresentado após Q95. Confirmado em 2026-09-10T17:47:24.811331Z. Entrevista funcional concluída; preparação da revisão do catálogo autorizada. A pausa de catálogo permanece até aprovação e reconciliação. Nenhuma aprovação de publicação foi inferida.

## Revisão publicada após Gestão de Tempo

Mário Tinelli aprovou o catálogo completo, os quatro documentos e as quatro publicações em etapas explícitas. A descrição de #1014493 foi publicada e relida: status New e relações preservados, sem divergência ou conteúdo externo alterado. Registro da revisão em ../../scopes/2026-09-09-nexum-scope/requirements-time-review.json; operações remotas anteriores preservadas como histórico. Concluído em 2026-09-10T19:09:37.970937Z.

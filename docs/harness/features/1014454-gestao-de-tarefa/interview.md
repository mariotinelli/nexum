# Entrevista — Gestão de Tarefa (#1014454)

## Evidências e árvore inicial

Fontes: design-new-task, design-edit-task, design-guide, design-task-detail e design-project-detail. Relação 662 confirmada: Gestão de Projeto bloqueia Gestão de Tarefa; status New preservado. Busca em nomes de arquivos app não encontrou classes de Task/Tarefa/Comment/Comentario para resolver lacunas funcionais.

Guia e catálogo aprovados: quatro situações Pendente/Em andamento/Bloqueada/Concluída; prioridades Baixa/Média/Alta/Urgente; autor automático; conclusão registra data e reabertura a remove. Criação por gestores/membros autorizados já aprovada no catálogo; remoção de participante responsável com confirmação deixa tarefas sem responsável. Integrações de cronômetro e horas pertencem a Gestão de Tempo.

Protótipo permite edição por gestor ou responsável, oferece troca de projeto, comentários condicionados à edição e filtra tarefas arquivadas do progresso. Os efeitos finais de permissões, transferência e colaboração precisam de decisão. Fronteira Q39–Q48. Descendentes: transferência de conteúdo/responsável se Q40 permitir mudança; alcance da reatribuição e perda do próprio acesso conforme Q39; formato de edição conforme Q46 apenas se houver efeito funcional não resolvido. Nenhuma decisão técnica solicitada.

## Q39 — Permissões do autor e do responsável

Gestores e membros participantes podem criar e atribuir tarefas a qualquer participante ativo, mas depois somente gestores do projeto e o responsável atual podem editar todos os campos, mudar situação e arquivar? O autor, se não for gestor nem responsável, fica somente com consulta e colaboração permitida.

Recomendação: Sim, seguindo a autorização gestor ou responsável do protótipo, sem criar privilégio permanente para o autor.

Estado: blocking. Resposta: aguardando.

## Q40 — Mudança de projeto

Uma tarefa pode mudar de projeto depois de criada?

Recomendação: Não no MVP: manter o projeto fixo após criar, preservando o contexto de acesso e dos registros da tarefa. O protótipo apresenta o campo editável, mas não define os efeitos de uma transferência.

Estado: blocking. Resposta: aguardando.

## Q41 — Datas das tarefas

Data inicial e Prazo são opcionais e independentes, aceitam datas passadas e exigem prazo igual ou posterior ao início quando ambas existirem?

Recomendação: Sim. A retirada de datas aprovada anteriormente vale apenas para projetos.

Estado: blocking. Resposta: aguardando.

## Q42 — Estimativa

A estimativa deve ser opcional e, quando preenchida, aceitar somente minutos inteiros maiores que zero?

Recomendação: Sim. Campo vazio significa sem estimativa; zero, negativos e frações são recusados, conforme o campo em minutos da referência.

Estado: blocking. Resposta: aguardando.

## Q43 — Responsável desativado

Uma conta desativada deve permanecer como responsável nas tarefas existentes, identificada como inativa, mas não poder receber novas atribuições enquanto inativa?

Recomendação: Sim, preservando as atribuições existentes. Remover a pessoa do projeto continua seguindo a regra já aprovada de aviso, confirmação e tarefas sem responsável.

Estado: blocking. Resposta: aguardando.

## Q44 — Efeito do arquivamento

Arquivar deve retirar a tarefa das listas de trabalho, quadro e cálculo de progresso do projeto, mantendo seu detalhe e registros acessíveis somente para consulta aos participantes?

Recomendação: Sim, conforme a filtragem do protótipo. Sem reativação de tarefas nesta entrega; a tarefa arquivada deixa de compor tanto o total quanto as concluídas usadas no percentual.

Estado: blocking. Resposta: aguardando.

## Q45 — Comentários

Qualquer participante ativo pode comentar, inclusive em tarefa concluída, e editar ou excluir somente os próprios comentários, desde que tarefa e projeto não estejam arquivados?

Recomendação: Sim, separando colaboração da permissão de editar a tarefa. Excluir pede confirmação; arquivamento mantém comentários somente para consulta.

Estado: blocking. Resposta: aguardando.

## Q46 — Formatação dos textos

Descrição e comentários devem permitir quebras de linha, negrito, itálico, listas e links?

Recomendação: Sim, como formatação básica; sem HTML livre, imagens ou anexos. O guia pede formatação básica, mas o protótipo demonstra principalmente quebras de linha.

Estado: blocking. Resposta: aguardando.

## Q47 — Abrangência do histórico

Além de situação, responsável, prioridade, prazo, estimativa, conclusão e reabertura, registrar também alterações de título, descrição, data inicial e arquivamento?

Recomendação: Sim, com autor, data/hora e valores anteriores/novos quando aplicáveis, mantendo a criação e a ordem cronológica. Salvar sem alteração não gera evento.

Estado: blocking. Resposta: aguardando.

## Q48 — Edição simultânea

Se outra pessoa alterar a tarefa enquanto o formulário estiver aberto, devemos impedir que o salvamento sobrescreva silenciosamente essa alteração?

Recomendação: Sim: informar que a tarefa foi atualizada e pedir revisão antes de salvar novamente, preservando o texto digitado para comparação.

Estado: blocking. Resposta: aguardando.


## Respostas Q39–Q48 — 2026-09-10T13:00:40.971157Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q39

Resposta literal: não, apenas gestores criam tarefas. qualquer participante pode atribuir para qualquer participante, inclusive para ele mesmo. apenas gestores gerenciam tarefas, editar, etc.

Decisão: Somente gestores criam e gerenciam tarefas; atribuição é permitida a qualquer participante para qualquer participante, inclusive para si. Alcance sobre alteração de situação ainda precisa ser explicitado.

### Q40

Resposta literal: concordo, neste mvp nao.

Decisão: Não permitir trocar o projeto de uma tarefa após criação neste MVP.

### Q41

Resposta literal: concordo

Decisão: Datas de tarefas opcionais e independentes, aceitando passado; prazo igual ou posterior ao início quando ambas existirem.

### Q42

Resposta literal: a estimativa vai seguir o padrão de horas, aceitando inteiros maiores que 0 e no máximo 6. Se colocou 4.25, equivale a 4h e 15m, precisa existir um calculo para isso

Decisão: Estimativa em horas, maior que zero e no máximo seis; 4.25 equivale a 4h15min. A expressão inteiros conflita com o exemplo decimal; incremento/precisão precisa ser confirmado.

### Q43

Resposta literal: concordo

Decisão: Preservar responsável inativo nas tarefas existentes, identificando inatividade; impedir novas atribuições a contas inativas.

### Q44

Resposta literal: concordo

Decisão: Arquivadas saem de listas de trabalho, quadro e numerador/denominador do progresso; detalhe e registros permanecem somente consulta por participantes, sem reativação nesta entrega.

### Q45

Resposta literal: concordo

Decisão: Qualquer participante ativo pode comentar, inclusive em tarefa concluída; editar/excluir somente próprios comentários enquanto projeto e tarefa não arquivados; exclusão confirmada.

### Q46

Resposta literal: sim, a ideia é que seja aqueles editores tipo rich editor, que pode inserir imagem, praticamente um edit markdown mesmo

Decisão: Editor de texto rico/Markdown com formatação e inserção de imagens em descrição e comentários. Substitui a restrição anterior sem imagens; limites da inclusão de imagens precisam de confirmação.

### Q47

Resposta literal: concordo

Decisão: Histórico também registra título, descrição, data inicial e arquivamento, além dos eventos previstos; autor, data/hora, valores anteriores/novos quando aplicáveis, ordem cronológica; salvar sem alterações não gera evento.

### Q48

Resposta literal: concordo

Decisão: Impedir sobrescrita silenciosa após edição concorrente, informar atualização e pedir revisão preservando texto digitado.

Q39, Q42 e Q46 têm descendentes em aberto. Pausa de avanço para revisão do catálogo; demais esclarecimentos independentes podem continuar. Sem atualização remota.

## Fronteira após Q39–Q48

### Q49 — Quem altera a situação

A exclusividade dos gestores também vale para mudar situação, concluir e reabrir tarefas?

Recomendação: Sim, seguindo sua definição de que apenas gestores gerenciam tarefas. Participantes continuam podendo atribuir e comentar. Isso também restringe as ações de situação em Minhas Tarefas e no Quadro; a execução por cronômetro precisará respeitar essa distinção na Feature responsável.

Estado: blocking. Resposta: aguardando.

### Q50 — Horas decimais e conversão

Podemos aceitar estimativa opcional em horas decimais, com até duas casas, maior que zero e até 6, convertendo para horas/minutos e arredondando ao minuto mais próximo?

Recomendação: Sim: 4,25 → 4h15min; 4,5 → 4h30min; 4,10 → 4h06min. A parte decimal representa uma fração da hora, não minutos escritos após a vírgula; aceitar ponto ou vírgula na entrada.

Estado: blocking. Resposta: aguardando.

### Q51 — Retirar a atribuição

Além de atribuir a qualquer participante ativo, qualquer participante pode deixar a tarefa sem responsável, inclusive se concluída, desde que tarefa e projeto não estejam arquivados?

Recomendação: Sim. Atribuição não concede permissão de editar os demais dados; alterar responsável aparece no histórico. Arquivadas permanecem somente para consulta.

Estado: blocking. Resposta: aguardando.

### Q52 — Imagens no editor

A inclusão deve abranger imagens dentro da descrição e dos comentários, por upload ou colagem no editor, mantendo fora do MVP anexos independentes e outros tipos de arquivo?

Recomendação: Sim, com editor visual de texto rico compatível com a formatação aprovada. Isso inclui imagens no conteúdo sem ampliar para uma área geral de anexos.

Estado: blocking. Resposta: aguardando.


## Respostas Q49–Q52 — 2026-09-10T13:04:49.195049Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q49

Resposta literal: Vamos seguir na ideia de que ngm vai poder mudar a situação da tarefa manualmente, tem que ser semrpe por alguma ação.

Decisão: Ninguém altera diretamente a situação da tarefa; mudanças decorrem de ações. Ações, gatilhos e permissões precisam ser definidos; não assumir que apenas gestores acionam mudanças nem que todas dependem do cronômetro.

### Q50

Resposta literal: sim

Decisão: Estimativa opcional em horas decimais com até duas casas, maior que zero e até seis horas; aceitar ponto/vírgula, converter para horas/minutos arredondando ao minuto mais próximo. 4,25=4h15min; 4,5=4h30min; 4,10=4h06min.

### Q51

Resposta literal: sim

Decisão: Qualquer participante pode retirar a atribuição, inclusive de tarefa concluída, enquanto tarefa e projeto não arquivados; registrar no histórico sem conceder edição de outros campos.

### Q52

Resposta literal: vamos colocar nesse mvp, para inserir anexos na tarefa tbm, mas nao entra nessa parte da descrição da tarefa

Decisão: Incluir anexos de tarefa no MVP em área própria, separada da descrição. A resposta amplia o escopo; relação com imagens no editor, permissões e limites de arquivos precisam ser confirmados.

Q49 substitui edição direta de situação por ações, com fronteira de gatilhos/permissões ainda em aberto. Q52 inclui anexos separados da descrição, substituindo a exclusão geral anterior. Revisão de catálogo permanece pendente; nenhum avanço de publicação.

## Fronteira após Q49–Q52

### Q53 — Ações que mudam a situação

Podemos substituir o seletor de situação por ações explícitas: Iniciar tarefa → Em andamento; Bloquear → Bloqueada; Retomar → Em andamento; Concluir → Concluída; Reabrir → Pendente; Devolver à fila → Pendente?

Recomendação: sim, exibindo somente ações válidas para a situação atual. Pausar um cronômetro, por si só, não muda a situação da tarefa. O conjunto de ações deve ser confirmado antes de detalhar permissões e integração com execução; a recomendação não trata alteração de um campo como uma ação de negócio suficiente.

Estado: blocking. Resposta: aguardando.

### Q54 — Imagens no editor e anexos

Além da área própria de Anexos, o editor da descrição e dos comentários continua permitindo imagens inseridas no conteúdo, como solicitado em Q46?

Recomendação: sim: imagens fazem parte do conteúdo editado; arquivos anexados ficam em uma seção separada da tarefa. A resposta Q52 não foi interpretada como revogação silenciosa das imagens pedidas anteriormente.

Estado: blocking. Resposta: aguardando.

### Q55 — Permissões de anexos

Qualquer participante ativo pode anexar e baixar arquivos, inclusive em tarefa concluída, mas excluir somente os próprios anexos mediante confirmação? Em tarefa ou projeto arquivado, permitir apenas consulta e download?

Recomendação: sim, seguindo a regra de colaboração dos comentários e preservando consulta após arquivamento. Quem não participa não acessa os arquivos.

Estado: blocking. Resposta: aguardando.

### Q56 — Tipos e tamanho de anexos

Quais tipos e tamanho máximo por arquivo devemos aceitar?

Recomendação: PDF, imagens, documentos de texto, planilhas e ZIP, até 20 MB por arquivo, cobrindo os materiais comuns de uma equipe. Outros tipos ou limites podem ser definidos pelo usuário.

Estado: blocking. Resposta: aguardando.

Descendentes de Q53: autorização para acionar as mudanças, conjunto final de transições e vínculo com cronômetro. Descendentes de Q54/Q56: somente detalhes funcionais de arquivos que as respostas deixarem em aberto. Nenhum mecanismo técnico será entrevistado.

## Respostas Q53–Q56 — 2026-09-10T13:32:35.475433Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q53

Resposta: Não vamos ter Retomar, pois é o mesmo que Iniciar. Não vamos ter Bloquear nem esse status. Concluir passa a Finalizar. Não existem Devolver à fila nem Reabrir. Ações finais: Iniciar: Em andamento; Finalizar: Finalizada; Cancelar: Cancelada; Pausar: Pausada; Arquivar: Arquivada.

Decisão: Novo fluxo exclusivo por ações: Iniciar → Em andamento; Finalizar → Finalizada; Cancelar → Cancelada; Pausar → Pausada; Arquivar → Arquivada. Remover Retomar, Bloquear/Bloqueada, Concluir/Concluída, Devolver à fila e Reabrir. A lista final usa Finalizada, prevalecendo sobre a menção intermediária Finalizado. Situação inicial, origens permitidas, permissões e efeitos nas integrações ainda precisam ser esclarecidos.

### Q54

Resposta: concordo

Decisão: Manter imagens no editor da descrição e comentários, além da área separada de Anexos.

### Q55

Resposta: concordo

Decisão: Qualquer participante ativo pode anexar e baixar arquivos, inclusive em tarefa finalizada; excluir somente próprios anexos mediante confirmação. Em tarefa ou projeto arquivado, somente consulta/download; acesso restrito à participação.

### Q56

Resposta: concordo

Decisão: Aceitar anexos PDF, imagens, documentos de texto, planilhas e ZIP, até 20 MB por arquivo.

O novo fluxo substitui situações/transições antigas e amplia os impactos da revisão para consumidores como Quadro, Minhas Tarefas, Gestão de Tempo e Painel Gerencial. Catálogo e operações remotas permanecem preservados até esclarecimento e aprovação da revisão. Q53 requer descendentes; Q54–Q56 resolvidas.

## Fronteira após Q53–Q56

### Q57 — Situação inicial e ações permitidas

A tarefa continua nascendo Pendente e podemos aplicar a tabela abaixo?

| Situação atual | Ações disponíveis |
| --- | --- |
| Pendente | Iniciar, Finalizar, Cancelar, Arquivar |
| Em andamento | Pausar, Finalizar, Cancelar, Arquivar |
| Pausada | Iniciar, Finalizar, Cancelar, Arquivar |
| Finalizada | Arquivar |
| Cancelada | Arquivar |
| Arquivada | Nenhuma |

Recomendação: sim. Mantém Pendente como início, Iniciar também atende à retomada de uma tarefa pausada e não permite reabrir tarefas finalizadas, canceladas ou arquivadas.

Estado: blocking. Resposta: aguardando.

### Q58 — Quem executa cada ação

Iniciar, Pausar e Finalizar podem ser executados pelo responsável atual e pelos gestores; Cancelar e Arquivar ficam exclusivos dos gestores?

Recomendação: sim. Gestores continuam exclusivos na criação e edição dos dados, enquanto o responsável executa seu trabalho. Qualquer participante mantém a permissão já aprovada para atribuir/desatribuir tarefas.

Estado: blocking. Resposta: aguardando.

### Q59 — Relação com o cronômetro

Podemos entregar essas ações de situação na Gestão de Tarefa e deixar sua integração com o cronômetro para Gestão de Tempo, sem exigir cronômetro para mudar a situação nesta entrega?

Recomendação: sim, mantendo as duas entregas do catálogo. A ação de negócio muda a situação; a integração de registrar horas e controlar execução será definida e entregue na Feature responsável.

Estado: blocking. Resposta: aguardando.

### Q60 — Colaboração após finalizar ou cancelar

Tarefas finalizadas continuam aceitando comentários e anexos, como já aprovado, enquanto canceladas ficam somente para consulta, exceto pela ação Arquivar do gestor?

Recomendação: sim. Canceladas não permitem editar dados, atribuir ou colaborar; o gestor pode arquivá-las. Finalizadas mantêm a atribuição permitida em Q51 e as demais permissões já aprovadas, sem reabertura. Arquivadas permanecem somente para consulta/download.

Estado: blocking. Resposta: aguardando.

### Q61 — Progresso e atraso

Devemos excluir canceladas e arquivadas do cálculo de progresso e de atraso, mantendo pendentes, em andamento e pausadas como trabalho ainda não finalizado?

Recomendação: sim. Progresso = Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas), com 0% quando não houver tarefas nesse conjunto. Somente pendentes, em andamento e pausadas podem ficar atrasadas quando seu prazo passar.

Estado: blocking. Resposta: aguardando.

Descendentes aguardam Q57/Q58 para fechar permissões por situação e reflexos no Quadro/Minhas Tarefas; Q59 determina fronteira funcional com Gestão de Tempo. Não solicitar mecanismos técnicos de implementação.

## Respostas Q57–Q61 — 2026-09-10T13:37:52.476182Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q57

Resposta: Em andamento: Pausar ou Finalizar. Finalizada não tem nenhuma ação. Arquivada pode Ativar ou Desarquivar, voltando para Pendente. O resto eu concordo.

Decisão: Tarefa nasce Pendente. Pendente: Iniciar/Finalizar/Cancelar/Arquivar. Em andamento: Pausar/Finalizar. Pausada: Iniciar/Finalizar/Cancelar/Arquivar. Finalizada: nenhuma ação de situação. Cancelada: Arquivar. Arquivada: Desarquivar → Pendente. Usar o nome Desarquivar dentre as alternativas dadas. Inclusão de desarquivamento substitui exclusão anterior; sua permissão e efeito sobre cancelada arquivada precisam de confirmação.

### Q58

Resposta: concordo

Decisão: Responsável atual e gestores podem Iniciar, Pausar e Finalizar quando a situação permitir. Cancelar e Arquivar somente gestores. Criação e edição de dados somente gestores; atribuição/desatribuição segue participação.

### Q59

Resposta: concordo

Decisão: Ações de situação funcionam na Gestão de Tarefa sem exigir cronômetro. Gestão de Tempo entrega posteriormente a integração de execução/horas.

### Q60

Resposta: concordo

Decisão: Finalizadas mantêm comentários, anexos e atribuição conforme aprovado, sem ações de situação. Canceladas ficam somente consulta, exceto Arquivar pelo gestor; sem edição, atribuição ou colaboração.

### Q61

Resposta: concordo

Decisão: Progresso = Finalizadas/(Pendentes+Em andamento+Pausadas+Finalizadas), zero sem tarefas nesse conjunto. Canceladas e arquivadas excluídas do progresso e atraso; apenas Pendentes/Em andamento/Pausadas ficam atrasadas pelo prazo.

Finalizada sem ação foi interpretada no contexto explícito da tabela de situações; Q60 mantém colaboração/atribuição. Q57 inclui desarquivamento, antes excluído. O percurso Cancelada → Arquivada → Pendente surge das transições e será confirmado sem presumir exceção.

## Q62 — Desarquivamento

Desarquivar deve ser exclusivo dos gestores, apenas em projeto ativo, retornando sempre a Pendente, inclusive quando a tarefa estava Cancelada antes de ser arquivada?

Recomendação: sim, mantendo a permissão de gestão do arquivamento e a regra de retorno para Pendente que você definiu. O caminho Cancelada → Arquivada → Pendente permite voltar a trabalhar nessa tarefa, sem uma ação direta Reabrir.

Estado: blocking. Resposta: aguardando.

## Resposta Q62 — 2026-09-10T13:38:56.883789Z

Resposta literal: concordo.

Proveniência: Mário Tinelli, nesta conversa.

Decisão: Desarquivar somente por gestores, em projeto ativo, sempre retornando a Pendente, inclusive se cancelada antes do arquivamento. Q62 resolvida.

## Auditoria do entendimento

Q39–Q62 reconciliadas. Papéis, transições por ações, datas, estimativa, atribuição, colaboração, anexos, histórico, concorrência, arquivamento/desarquivamento e indicadores definidos. Imagens no conteúdo e anexos separados incluídos por decisão explícita, substituindo exclusões anteriores. Ações de tarefa independem de cronômetro nesta entrega; Gestão de Tempo integra a execução posteriormente. Fontes antigas com Bloqueada, Concluída, reabertura e edição direta de situação serão reconciliadas na revisão do catálogo. Não há descendente funcional conhecido sem resposta; confirmação explícita do entendimento ainda aguardada. Pausa para aprovação do catálogo revisado permanece vigente.

## Confirmação explícita do entendimento — 2026-09-10T13:42:06.815366Z

Resposta literal: sim. Mário Tinelli confirmou a síntese de Gestão de Tarefa e a preparação da revisão completa do catálogo. Sem lacunas funcionais conhecidas; aprovação da projeção revisada ainda pendente.

## Aprovação do catálogo revisado — 2026-09-10T13:48:21.045751Z

Mário Tinelli respondeu literalmente "sim" à apresentação integral de catalog-task-review.md. Aprovação catalog-task-review-001, SHA-256 18de3f933af33e0ee309b4a954f0dafc5c1974bef9090654563884d43906951e. Pausas resolvidas; entrega herdada reconciliada. Issue #1014454 relida em New, descrição inicial inalterada e relação 662 preservada. Operações concluídas permanecem concluídas. Entrevista pronta para redação do requisito completo.

## Requisito proposto e auditoria final — 2026-09-10T13:56:28.689551Z

Q44, Q45, Q51 e Q55 preservadas como formulações históricas reabertas e resolvidas pelas decisões posteriores Q57–Q62. Atribuição/colaboração respeitam somente consulta de Cancelada; Desarquivar é permitido conforme Q62. Outros descendentes anotados como pendentes nas rodadas antigas foram resolvidos nas respostas posteriores. Sem lacunas funcionais, contradições ou perguntas a terceiros pendentes.

feature.md contém todas as seções do contrato e 26 critérios de aceite; referências locais verificadas, estados e transições validados e bloco de catálogo sincronizado. SHA-256 do requisito proposto: 7938ff46044947c0fa2d66c844dcd8a900d82505116d6694bcc08598cab2781e. Aguardando aprovação explícita do documento completo.

## Correção explícita — 2026-09-10T14:08:05.421145Z

Mário Tinelli: "correção: Iniciar, Pausar e Finalizar, apenas o usuário responsavel". Substitui Q58: somente o responsável atual executa essas ações; gestor somente quando também responsável. Sem responsável, exige atribuição válida antes de executar. Corrigidos matriz, história, regra, exceção e CA10. Não há ambiguidade funcional adicional. Catálogo completo corrigido e requisito aguardam aprovação conjunta; publicação não autorizada.

## Aprovação conjunta — 2026-09-10T14:14:32.187427Z

Mário Tinelli respondeu "aprovado" ao catálogo completo corrigido e ao requisito. Aprovações catalog-responsible-only-001 e requirement-task-001 registradas; requisito SHA-256 177bf15d5ad696debaaf5d93261998b004e8f1cef5f9f6918b74ebd4660145d4. Apenas rótulos editoriais de aprovação atualizados. Pausas resolvidas e requisito aprovado; preparar a prévia completa da publicação, sem alterar o status New.

## Prévia de publicação — 2026-09-10T14:15:54.451129Z

Descrição completa em publication-preview.md; payload exato em publish-payload.json, SHA-256 89b99b34f37500e0742409d76df12a2b9e2c6fcdc2462538b2293cd3f32c5989. Atualizar somente description da issue #1014454; status New preservado. Sem conteúdo humano externo ou divergências internas; relação blocks:1014450:1014454 (662) já existente, nenhuma relação a criar. Aguardar aprovação explícita da publicação.

## Publicação e conclusão — 2026-09-10T14:22:13.587559Z

Mário Tinelli respondeu "sim" à prévia completa. Aprovação publish-task-001 persistida antes da atualização; Redmine confirmou, e a releitura verificou descrição aprovada, status New e relação 662. Operações e fases concluídas, estados e transições válidos; nenhuma pendência funcional. Requisito pronto para planejamento técnico.

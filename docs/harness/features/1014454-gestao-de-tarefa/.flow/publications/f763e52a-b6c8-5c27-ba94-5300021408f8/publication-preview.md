<!-- project-flow:start -->
## Objetivo

Permitir que gestores planejem e mantenham tarefas em seus projetos, que responsáveis executem as ações de trabalho permitidas e que participantes distribuam responsabilidades e colaborem no detalhe. A entrega organiza dados, prazos, estimativas, situações e registros em uma interface WEB em português, com rastreabilidade e acesso limitado à participação no projeto.

## Resultado esperado

Uma tarefa pode ser criada, consultada, editada, atribuída e acompanhada por ações explícitas de situação, com comentários, imagens, anexos e histórico. A aba de tarefas e o progresso por quantidade ficam integrados ao projeto. As ações funcionam sem exigir cronômetro; execução cronometrada e registro de horas pertencem à Gestão de Tempo.

## Atores e permissões

As permissões exigem conta ativa e participação atual no projeto. Projeto arquivado permite somente consulta de seu conteúdo; reativá-lo pertence à Gestão de Projeto.

| Operação | Quem pode executar | Limite |
| --- | --- | --- |
| Consultar tarefa e registros; baixar anexos | Qualquer participante | Inclui finalizadas, canceladas e arquivadas |
| Criar e editar dados da tarefa | Gestores | Projeto ativo; canceladas e arquivadas não admitem edição |
| Atribuir ou deixar sem responsável | Qualquer participante | Projeto ativo; tarefa pendente, em andamento, pausada ou finalizada; nova atribuição somente a participante ativo |
| Iniciar, Pausar e Finalizar | Somente o responsável atual | Projeto ativo e ação permitida pela situação |
| Cancelar e Arquivar | Gestores | Projeto ativo e ação permitida pela situação |
| Desarquivar | Gestores | Tarefa arquivada em projeto ativo; retorna a Pendente |
| Comentar e anexar | Qualquer participante | Projeto ativo; tarefa pendente, em andamento, pausada ou finalizada |
| Editar/excluir comentário ou excluir anexo | Autor do respectivo registro | Mesmas restrições de colaboração; exclusão confirmada |

Ser autor da tarefa não concede privilégios permanentes. Ser responsável permite as ações indicadas, sem conceder edição dos demais dados. Administradores não ganham acesso automático nem gestão de tarefas: aplicam-se sua participação e papel no projeto. Contas inativas não acessam o sistema.

## Fluxo principal

**Criação:** o gestor abre Nova tarefa pela lista ou projeto, seleciona um projeto ativo que gerencia e informa Título. Pode preencher Descrição, Responsável, Data inicial, Prazo e Estimativa em horas. A tarefa inicia Pendente, prioridade Média e autor automático; pode escolher outra prioridade fixa. Após validar e criar, abrir o detalhe com confirmação. Cancelar o formulário não cria a tarefa e retorna à lista de origem.

**Consulta:** um participante abre o detalhe pelo projeto ou pelas consultas que consumirem esta Feature. Apresentar título, projeto, descrição, situação, prioridade, responsável, autor, datas, estimativa e data de finalização quando existente. Oferecer comentários, área própria de anexos e histórico. Ações respeitam simultaneamente papel, situação da tarefa e estado do projeto.

**Edição:** o gestor altera os dados atuais e salva. Projeto e autor permanecem fixos; situação não é campo editável. Validar e retornar ao detalhe com confirmação. Cancelar mantém os dados anteriores. Finalizadas continuam admitindo edição dos dados por gestores, atribuição e colaboração, sem ações de situação.

**Atribuição:** qualquer participante seleciona qualquer participante ativo do mesmo projeto, inclusive a si, ou Sem responsável. A mudança vale imediatamente para as ações do responsável e aparece no histórico, sem mudar as permissões de edição dos dados.

**Situação:** executar somente as combinações abaixo. O resultado atualiza situação e histórico. Finalizar registra automaticamente data/hora. Arquivar exige confirmação; cancelar a confirmação preserva a tarefa. Desarquivar sempre retorna a Pendente.

| Situação atual | Ações e resultados permitidos |
| --- | --- |
| Pendente | Iniciar → Em andamento; Finalizar → Finalizada; Cancelar → Cancelada; Arquivar → Arquivada |
| Em andamento | Pausar → Pausada; Finalizar → Finalizada |
| Pausada | Iniciar → Em andamento; Finalizar → Finalizada; Cancelar → Cancelada; Arquivar → Arquivada |
| Finalizada | Nenhuma ação de situação |
| Cancelada | Arquivar → Arquivada |
| Arquivada | Desarquivar → Pendente |

**Colaboração:** participantes publicam comentários com texto rico, consultam-nos em ordem cronológica com autor e horário e editam/excluem somente os próprios. Descrição e comentários permitem quebras de linha, negrito, itálico, listas, links e imagens no conteúdo. Anexos ficam separados da descrição: participantes adicionam e baixam arquivos e excluem somente os próprios mediante confirmação.

**Projeto:** apresentar suas tarefas com acesso ao detalhe e progresso por quantidade. Arquivadas deixam as listas de trabalho e o quadro, mantendo detalhe para consulta autorizada. Calcular progresso e atraso segundo R13. Consulta transversal, Minhas Tarefas e Quadro do Projeto são entregas próprias que consomem estas regras.

## Fluxos alternativos e exceções

- Sem participação, com conta inativa ou sem permissão: recusar a operação, inclusive por acesso direto ou tela previamente aberta. Reavaliar papel e atribuição atuais ao executar ações.
- Projeto arquivado: preservar consulta/download e impedir todas as mutações da tarefa, inclusive Desarquivar, atribuir, comentar e anexar.
- Cancelada: somente consulta/download, exceto Arquivar por gestor. Arquivada: somente consulta/download, exceto Desarquivar por gestor em projeto ativo.
- Sem responsável: ninguém pode Iniciar, Pausar ou Finalizar até uma atribuição válida. Participantes podem atribuir conforme as regras gerais; gestores mantêm apenas as demais operações permitidas por seu papel e pela situação.
- Responsável desativado: manter atribuição e indicar inatividade; impedir novas atribuições a contas inativas.
- Remoção de participante responsável: informar impacto e pedir confirmação. Confirmar remove vínculo e deixa suas tarefas sem responsável, inclusive finalizadas, canceladas e arquivadas, preservando comentários, horas e histórico anteriores. Cancelar mantém vínculo e atribuições. Essa consequência da gestão de participantes não autoriza editar diretamente tarefas de somente consulta.
- Dados inválidos: impedir salvar, explicar erros e preservar preenchimento. Tipo de arquivo não aceito ou tamanho acima do limite impede anexar, com motivo e nova tentativa.
- Edição simultânea: se outra pessoa atualizar a tarefa durante a edição, impedir sobrescrita silenciosa, informar a atualização e pedir revisão antes de novo salvamento, preservando o texto digitado para comparação.
- Sem registros ou tarefas a apresentar: mostrar estado vazio apropriado. Operações têm carregamento; falhas não indicam sucesso e permitem nova tentativa.

## Regras de negócio

R1. Consulta depende de participação; criação e edição dos dados são exclusivas de gestores. Atribuição e colaboração obedecem à matriz de permissões. Autor, responsável e administrador não recebem poderes adicionais aos descritos.

R2. Projeto e Título são obrigatórios. Projeto deve estar ativo e ser gerenciado pelo criador. Autor é automático e imutável. Projeto não pode ser trocado depois da criação neste MVP.

R3. Situação inicial Pendente e prioridade inicial Média. Prioridades fixas: Baixa, Média, Alta e Urgente. Descrição, responsável, datas e estimativa são opcionais; ausência de responsável ou estimativa é apresentada como tal.

R4. Data inicial e Prazo são independentes e aceitam passado. Quando ambas existirem, Prazo deve ser igual ou posterior à Data inicial. A retirada de datas dos projetos não retira as datas das tarefas.

R5. Estimativa aceita horas decimais, até duas casas, maior que zero e no máximo 6. Aceitar ponto ou vírgula; a fração decimal representa parte de uma hora. Converter para horas/minutos arredondando ao minuto mais próximo: 4,25 → 4h15min; 4,5 → 4h30min; 4,10 → 4h06min. Campo vazio significa Sem estimativa, não zero.

R6. Nova atribuição exige participante ativo do mesmo projeto. Qualquer participante pode atribuir a si ou a outro, ou retirar atribuição, inclusive em finalizada. Responsável inativo existente permanece identificado até reatribuição ou remoção da participação. Remoção confirmada retira suas atribuições e preserva registros anteriores.

R7. Situação muda exclusivamente pelas ações da tabela. Somente o responsável atual executa Iniciar/Pausar/Finalizar. Um gestor só executa essas três ações quando também for o responsável. Gestores executam Cancelar/Arquivar/Desarquivar. Somente ações válidas ficam disponíveis; outras transições são recusadas. Não há seletor de situação, mudança por arrastar, Bloquear/Bloqueada, Retomar, Reabrir ou Devolver à fila.

R8. Finalizar registra data/hora. Finalizada não permite ações de situação, inclusive Arquivar; mantém edição dos dados por gestores, atribuição e colaboração conforme as permissões. Esses atos não alteram sua situação nem reabrem a tarefa.

R9. Cancelada e Arquivada são de somente consulta/download, com as exceções da tabela. Arquivar exige confirmação, retira das listas de trabalho, quadro e progresso e preserva registros. Desarquivar é exclusivo de gestores em projeto ativo e sempre retorna a Pendente, inclusive no percurso Cancelada → Arquivada → Pendente.

R10. Comentários têm conteúdo obrigatório, autor e horário e são apresentados cronologicamente. Participantes editam/excluem somente os próprios; exclusão exige confirmação. Descrição e comentários usam editor rico com imagens e a formatação aprovada. Sem comentários privados ou menções.

R11. Anexos ficam em área própria, separada da descrição. Aceitar PDF, imagens, documentos de texto, planilhas e ZIP, até 20 MB por arquivo. Participantes adicionam/baixam e excluem somente os próprios com confirmação. A restrição de acesso à tarefa também protege seus arquivos; finalizadas mantêm colaboração, canceladas/arquivadas permitem apenas download dos anexos.

R12. Histórico cronológico registra criação e mudanças de título, descrição, situação por ação, responsável, prioridade, data inicial, prazo, estimativa e arquivamento/desarquivamento. Informar autoria, data/hora e valores anteriores/novos quando aplicáveis, incluindo finalização. Salvar sem alterações não gera evento. Não sobrescrever silenciosamente edição concorrente.

R13. Progresso = Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas), em percentual; conjunto vazio resulta em 0%. Canceladas e arquivadas ficam fora de numerador e denominador. Atraso exige prazo anterior à data atual e situação Pendente, Em andamento ou Pausada; sem prazo não há atraso.

R14. As ações de tarefa não exigem cronômetro nesta entrega. Gestão de Tempo integrará execução e horas e exigirá encerrar ou descartar execução aberta antes de Finalizar/Arquivar quando permitidas e antes de arquivar o projeto. A integração não autoriza transições proibidas nem altera a matriz de papéis desta Feature.

## Dados percebidos pelo usuário

Projeto, título, descrição com imagens, situação, prioridade, responsável ou Sem responsável, indicação de responsável inativo, autor, Data inicial, Prazo, estimativa em horas com equivalente em horas/minutos ou Sem estimativa e data/hora de finalização. Comentários com autoria/horário, anexos identificáveis para download e histórico com mudanças. Formulários, ações, confirmações, validação e aviso de concorrência; tarefas, atraso e progresso no projeto. Horas realizadas e cronômetro serão integrados pela Gestão de Tempo.

## Critérios de aceite

CA1 — Como gestor de projeto ativo, ao criar com título e projeto válidos, gerar tarefa Pendente, prioridade Média e autor atual automático; abrir detalhe e confirmar. Membro ou administrador sem papel Gestor no projeto não pode criar. [R1–R3]

CA2 — Ao criar somente com campos obrigatórios, aceitar os opcionais vazios. Projeto/título ausentes ou projeto arquivado impedem criar, com mensagem e preenchimento preservado. Ao cancelar formulário, não criar tarefa. [R2–R3; criação]

CA3 — Como gestor autorizado, ao editar dados válidos, salvar e retornar ao detalhe; cancelar preserva dados anteriores. Trocar projeto/autor ou editar diretamente situação é recusado. Responsável sem papel Gestor não edita demais dados. [R1–R3, R7]

CA4 — Como participante ativo, ao abrir tarefa do projeto, mostrar dados e registros permitidos. Sem participação ou após perdê-la, impedir acesso à tarefa e anexos, inclusive por acesso direto ou tela já aberta. [R1, R11]

CA5 — Ao informar somente uma data, datas passadas ou prazo igual ao início, aceitar. Prazo anterior ao início quando ambos preenchidos impede salvar, com erro. [R4]

CA6 — Ao informar 4,25 ou 4.25, mostrar 4h15min; 4,5 resulta em 4h30min e 4,10 em 4h06min. Aceitar 6 e vazio; rejeitar zero, negativos, mais de 6 e mais de duas casas. Arredondar fração válida ao minuto mais próximo, como 0,01 → 0h01min. [R5]

CA7 — Como participante, ao atribuir a si, a outro participante ativo ou a Sem responsável, atualizar atribuição e histórico, inclusive em finalizada. Nova atribuição a não participante ou conta inativa é recusada. [R6, R12]

CA8 — Com responsável existente desativado, ao consultar, manter seu nome e indicar inatividade. Após reatribuição, as ações do responsável passam à pessoa atual sem conceder edição dos demais dados. [R1, R6]

CA9 — Para cada origem/ação da tabela, como pessoa autorizada em projeto ativo, ao executar, alcançar exatamente o destino indicado e registrar mudança. Combinações fora da tabela são recusadas; não oferecer seletor manual. [R7, R12]

CA10 — Como responsável atual, ao executar Iniciar/Pausar/Finalizar nas origens autorizadas, permitir a ação. Gestor que não seja responsável e demais participantes são impedidos; sem responsável, ninguém executa essas três ações até atribuição válida. Gestor também responsável pode executá-las. Cancelar/Arquivar/Desarquivar são recusadas para não gestores. [R7; exceções]

CA11 — Com Pendente, Em andamento ou Pausada, ao Finalizar, torná-la Finalizada e registrar data/hora. Depois, não oferecer ações de situação, inclusive Arquivar/Reabrir, mantendo edição por gestor, atribuição, comentários e anexos. [R8]

CA12 — Com Em andamento, ao tentar Cancelar ou Arquivar diretamente, recusar. Após Pausar, permitir ao gestor as ações previstas para Pausada. [R7]

CA13 — Com Cancelada, ao tentar editar, atribuir, comentar ou anexar, recusar; manter consulta/download e permitir ao gestor Arquivar. [R9–R11]

CA14 — Com origem que permite Arquivar, ao confirmar como gestor, arquivar, preservar registros e retirar das listas de trabalho, quadro e progresso. Cancelar a confirmação mantém situação e dados. [R9, R13]

CA15 — Com Arquivada em projeto ativo, ao Desarquivar como gestor, retornar a Pendente, inclusive se era Cancelada antes. Em projeto arquivado, recusar Desarquivar e demais mutações, mantendo consulta/download. [R9; exceções]

CA16 — Como participante autorizado, ao publicar comentário com formatação/imagens, preservar conteúdo e exibir autoria/horário cronologicamente. Impedir comentário vazio; editar somente o próprio e excluir o próprio mediante confirmação. Cancelar exclusão preserva o comentário. [R10]

CA17 — Como gestor autorizado, ao salvar descrição com quebras, negrito, itálico, listas, links e imagens, exibir o conteúdo no detalhe. Anexos permanecem em área separada. [R10–R11]

CA18 — Como participante autorizado, ao anexar PDF, imagem, documento de texto, planilha ou ZIP até 20 MB, disponibilizar para download. Tipo não aceito ou arquivo acima de 20 MB é recusado com motivo e nova tentativa. [R11]

CA19 — Ao excluir anexo próprio, pedir confirmação e remover após confirmar; cancelar preserva. Recusar excluir anexo alheio, inclusive por gestor; canceladas/arquivadas permitem somente consulta/download dos arquivos. [R11]

CA20 — Após criar ou alterar cada dado de R12, ao consultar histórico, mostrar evento cronológico com autoria, data/hora e anterior/novo quando aplicáveis. Salvar sem alterações não cria evento. [R12]

CA21 — Com formulário aberto e atualização posterior por outra pessoa, ao salvar, impedir sobrescrita silenciosa, informar atualização e preservar texto digitado para revisão antes de novo salvamento. [R12]

CA22 — Com 2 Finalizadas, 1 Pendente, 1 Em andamento, 1 Pausada, 1 Cancelada e 1 Arquivada, ao consultar progresso, mostrar 40%. Com somente canceladas/arquivadas ou nenhuma tarefa, mostrar 0%. [R13]

CA23 — Com prazo anterior à data atual, ao consultar atraso, contar apenas Pendentes, Em andamento e Pausadas. Prazo de hoje, futuro, ausente ou situações Finalizada/Cancelada/Arquivada não contam como atraso. [R13]

CA24 — Como gestor removendo participante responsável, ao confirmar impacto, deixar suas tarefas sem responsável em todas as situações e preservar comentários, horas e histórico anteriores. Cancelar mantém vínculo e atribuições. [R6; remoção]

CA25 — Sem integração de cronômetro, ao executar ação válida, mudar situação normalmente. Com Gestão de Tempo disponível e execução aberta, ao tentar Finalizar/Arquivar em origem permitida ou arquivar projeto, exigir encerrar/descartar execução. [R14; integração]

CA26 — Em desktop/mobile, ao usar formulários, comentários, anexos, ações e diálogos, manter teclado, labels, foco visível e mensagens acessíveis. Carregamento, vazio, erro e sucesso são distinguíveis; falhas preservam preenchimento para correção e nova tentativa. [Fluxos; guia]

## Dependências

Gestão de Projeto (#1014450) fornece projetos, participação, papéis e arquivamento; relação nativa 662 já registrada: #1014450 bloqueia #1014454. Esta Feature integra tarefas, progresso por quantidade e a consequência da remoção confirmada de participantes responsáveis.

Consulta de Tarefas, Gestão de Tempo, Minhas Tarefas, Quadro do Projeto e Painel Gerencial consomem dados, permissões e situações aqui definidos. Gestão de Tempo entrega execução/horas posteriormente; seus critérios de integração são verificados quando essa capacidade for entregue. Não há novo bloqueio de Gestão de Tarefa por esses consumidores.

## Dentro do escopo

Criação/edição por gestores, consulta por participantes, atribuição, datas/estimativa, fluxo fixo por ações, arquivamento/desarquivamento, editor rico com imagens, comentários, anexos separados, histórico, proteção contra sobrescrita concorrente, tarefas/progresso no projeto e remoção confirmada de responsáveis. Interface WEB em português, responsiva, com carregamento, vazio, erro, indisponibilidade e sucesso. Requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento.

## Fora do escopo

Transferência entre projetos, exclusão definitiva de tarefa, campos personalizados, workflow configurável, comentários privados, menções, notificações de negócio, dependências entre tarefas, sprints/backlog, aplicativo nativo e API pública. Consulta transversal, organização diária, quadro, cronômetro, apontamentos e painel permanecem nas Features responsáveis. Este requisito não estabelece biblioteca, armazenamento ou desenho técnico.

## Requisito canônico

Documento aprovado: docs/harness/features/1014454-gestao-de-tarefa/feature.md

Requisito aprovado por Mário Tinelli.
<!-- project-flow:end -->
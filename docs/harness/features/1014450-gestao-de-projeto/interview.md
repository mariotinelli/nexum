# Entrevista — Gestão de Projeto (#1014450)

## Evidências e árvore inicial

Fontes do catálogo: design-projects, design-new-project, design-guide, design-edit-project, design-users, design-project-detail e design-task-detail. Protótipo: criação por perfil gestor simulado; gestor principal e papéis Gestor/Membro; identificador em uso e prazo anterior ao início recusados; remoção de responsável recusada até reatribuir tarefas; consulta administrativa de vínculos sem abertura do projeto. Busca em app/Models, app/Enums e routes não encontrou implementação de projeto para resolver essas regras. O protótipo usa perfis e IDs ilustrativos, sem determinar a permissão inicial de criação no produto.

Relação 661 confirmada: #1014449 bloqueia #1014450. Status New preservado.

A fronteira contém Q21–Q28. Descendentes aguardam: participação do criador (Q21); efeitos da troca de gestor principal, remoção do próprio vínculo e perda do último gestor ativo (Q22 e Q27). Integrações com tarefas e tempo respeitam os responsáveis do catálogo; sem implementação nesta entrevista.

## Q21 — Quem pode criar projetos

O papel de gestor pertence a um projeto. Quem pode criar um projeto, inclusive o primeiro?

Recomendação: qualquer usuário autenticado e ativo pode criar, tornando-se gestor participante do novo projeto. Isso permite iniciar projetos sem depender de um papel que ainda não existe. É uma escolha a confirmar frente à indicação genérica criação por gestor do design.

Estado: blocking. Resposta: aguardando.

## Q22 — Gestor principal e demais gestores

O campo Gestor identifica um responsável principal, mas outros participantes podem ter papel Gestor com as mesmas permissões de editar dados/participantes, arquivar e reativar?

Recomendação: sim; um gestor principal obrigatório e outros gestores permitidos, com as mesmas permissões no projeto, conforme os dois controles da referência.

Estado: blocking. Resposta: aguardando.

## Q23 — Identificador

O identificador deve aceitar letras minúsculas sem acento, números e hífen, ser único incluindo projetos arquivados e ficar imutável após criar?

Recomendação: sim, usando projeto-exemplo como referência e mantendo uma identificação estável. Nomes podem se repetir; identificadores não.

Estado: blocking. Resposta: aguardando.

## Q24 — Datas

As datas continuam opcionais e independentes, aceitando datas passadas; quando ambas existirem, o prazo deve ser igual ou posterior ao início?

Recomendação: sim, conforme a validação do protótipo, sem impedir cadastro de projetos já iniciados.

Estado: blocking. Resposta: aguardando.

## Q25 — Listagem inicial

A lista deve iniciar em Todos, ordenar alfabeticamente por nome e manter o filtro Todos/Ativos/Arquivados durante a sessão de navegação?

Recomendação: sim, mantendo previsibilidade e o filtro inicial mostrado na referência.

Estado: blocking. Resposta: aguardando.

## Q26 — Consulta administrativa de vínculos

O modal Projetos do usuário deve mostrar projetos ativos e arquivados com nome, estado e papel, sem permitir abrir detalhes de um projeto do qual o administrador não participa?

Recomendação: sim, permitindo administrar vínculos visíveis sem conceder acesso ao conteúdo do projeto.

Estado: blocking. Resposta: aguardando.

## Q27 — Participantes desativados

Ao desativar uma conta, devemos preservar seus vínculos e papéis, identificando-a como inativa no projeto, sem permitir novas inclusões dessa conta enquanto inativa?

Recomendação: sim, preservando a composição existente sem permitir acesso. Se todos os gestores ficarem inativos, um administrador reativa uma dessas contas pela Gestão de Usuário para que a gestão do projeto possa ser retomada; não ganha acesso automático ao projeto.

Estado: blocking. Resposta: aguardando.

## Q28 — Remover participante responsável por tarefas

Quando a Gestão de Tarefa estiver disponível, a remoção de participante deve ser impedida enquanto existir tarefa atribuída a ele, inclusive concluída ou arquivada, exigindo reatribuição antes?

Recomendação: sim, conforme o bloqueio do protótipo e a regra de que o responsável pertence ao projeto. A integração entra com Gestão de Tarefa.

Estado: blocking. Resposta: aguardando.

## Respostas Q21–Q28 — 2026-09-10T12:04:52.107096Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q21

Resposta: apenas administradores

Decisão: Somente administradores podem criar projetos; substitui a recomendação de criação por qualquer usuário ativo.

### Q22

Resposta: concordo

Decisão: Um gestor principal obrigatório e outros participantes Gestor com as mesmas permissões de gestão.

### Q23

Resposta: deve ser gerado automaticamente, seguindo a ideia do youtrack ou jira, exemplos: Rem Soft Projeto Padrão → RSP; Rem Soft Tool → RST

Decisão: Identificador automático a partir do nome, com exemplos RSP e RST. Algoritmo, colisões e mutabilidade ainda precisam de definição; a resposta não aprova as demais partes da recomendação anterior.

### Q24

Resposta: remover datas do mvp

Decisão: Remover datas do MVP; alcance entre projeto e tarefas precisa ser esclarecido antes de revisar o catálogo.

### Q25

Resposta: concordo

Decisão: Lista inicia em Todos, ordem alfabética por nome e filtro persistido durante a sessão.

### Q26

Resposta: concordo

Decisão: Modal administrativo mostra projetos ativos e arquivados com nome, estado e papel, sem abrir detalhes sem participação.

### Q27

Resposta: concordo

Decisão: Preservar vínculos/papéis de contas desativadas, marcá-las inativas e impedir novas inclusões; administrador reativa gestor quando todos estiverem inativos, sem ganhar acesso ao projeto.

### Q28

Resposta: não impedir, apenas informe ao usuário e pergunte se ele quer remover mesmo assim.

Decisão: Remoção de participante responsável por tarefas exige aviso e confirmação, sem impedimento absoluto; destino das atribuições ainda precisa ser definido.

Q23, Q24 e Q28 têm descendentes em aberto. O catálogo permanece intacto enquanto seu impacto é esclarecido. Avanço pausado para revisão do catálogo conforme project-flow, sem adiamento solicitado pelo usuário.

## Fronteira após Q21–Q28

### Q29 — Alcance da retirada de datas

Remover datas apenas dos projetos ou também datas e prazos das tarefas, filtros e indicadores de atraso?

Recomendação: Apenas Data inicial e Prazo do projeto, preservando as datas das tarefas. A pergunta original era sobre projeto; o alcance global alteraria várias Features.

Estado: blocking. Resposta: aguardando.

### Q30 — Regra de geração do identificador

Podemos usar as iniciais das três primeiras palavras, ignorando de/da/do/das/dos/e, em maiúsculas e sem acentos; para nome de uma palavra usar até três primeiras letras e para duas usar as duas iniciais?

Recomendação: Sim: Rem Soft Projeto Padrão → RSP; Rem Soft Tool → RST; Financeiro → FIN; Portal Cliente → PC. Os exemplos guiam o comportamento, sem assumir regra específica de Jira ou YouTrack.

Estado: blocking. Resposta: aguardando.

### Q31 — Colisão e estabilidade do identificador

Se a sigla estiver em uso, inclusive por projeto arquivado, acrescentar número RSP2, RSP3 etc.; manter o código sem edição manual e sem mudar ao renomear o projeto?

Recomendação: Sim, garantindo código único e referência estável, gerada automaticamente.

Estado: blocking. Resposta: aguardando.

### Q32 — Tarefas após remover participante

Ao confirmar a remoção, as tarefas atribuídas à pessoa devem ficar sem responsável, preservando comentários, horas e histórico anteriores?

Recomendação: Sim, avisando essa consequência antes da confirmação. A pessoa perde acesso ao projeto; preservam-se os registros passados sem manter um responsável que deixou de participar.

Estado: blocking. Resposta: aguardando.

### Q33 — Administrador que cria para outra pessoa

Ao criar projeto e escolher outra pessoa como gestor principal, incluir o administrador criador apenas se ele for marcado na lista de participantes?

Recomendação: Sim, sem participação automática. Se não participar, concluir com sucesso e voltar à lista de projetos acessíveis, sem abrir o detalhe.

Estado: blocking. Resposta: aguardando.

### Q34 — Troca do gestor principal

Ao trocar o gestor principal, o anterior permanece como participante Gestor, salvo mudança explícita de papel ou remoção no mesmo formulário?

Recomendação: Sim, evitando perda de acesso implícita; o novo principal é incluído obrigatoriamente como Gestor.

Estado: blocking. Resposta: aguardando.

### Q35 — Remover o próprio vínculo ou papel de Gestor

Um gestor pode remover a própria participação ou virar Membro, mediante confirmação, desde que outro gestor principal ativo permaneça?

Recomendação: Sim. Se for o principal, deve indicar um substituto ativo na mesma alteração. Após salvar, aplicar imediatamente o novo acesso, sem reincluir a pessoa automaticamente.

Estado: blocking. Resposta: aguardando.


## Respostas Q29–Q35 — 2026-09-10T12:13:40.519549Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q29

Resposta literal: apenas dos projetos

Decisão: Retirar somente Data inicial e Prazo dos projetos; preservar datas de tarefas e seus filtros e indicadores.

### Q30

Resposta literal: sim, deve sigar esse ideia, mas sempre com 3 letras

Decisão: Identificador automático segue a ideia das iniciais, mas deve sempre conter exatamente três letras. Completar nomes curtos e escolher letras alternativas ainda exige definição.

### Q31

Resposta literal: não, ai deve mudar um pouco a regra das 3 letras geradas

Decisão: Colisões devem ser resolvidas escolhendo outra combinação de três letras, sem sufixo numérico. A resposta não confirma separadamente edição manual ou estabilidade ao renomear.

### Q32

Resposta literal: concordo

Decisão: Ao confirmar remoção do participante, suas tarefas ficam sem responsável, preservando comentários, horas e histórico; avisar a consequência antes da confirmação e revogar acesso ao projeto.

### Q33

Resposta literal: concordo

Decisão: Administrador criador que escolhe outro gestor principal somente participa se marcado; se não participar, concluir com sucesso e retornar à lista acessível sem abrir detalhes.

### Q34

Resposta literal: concordo

Decisão: Ao trocar gestor principal, o anterior permanece Gestor salvo alteração explícita de papel ou remoção; novo principal é participante Gestor obrigatório.

### Q35

Resposta literal: concordo

Decisão: Gestor pode remover a própria participação ou virar Membro mediante confirmação, mantendo outro principal ativo; se for principal, indicar substituto ativo na mesma alteração. Aplicar novo acesso imediatamente.

Retirada de datas limitada a projetos, sem alteração de datas de tarefas. Q30 e Q31 têm descendentes: composição sempre com três letras, colisões, nomes curtos, estabilidade e edição manual. Permanecem as pausas de revisão do catálogo.

## Fronteira após Q29–Q35

### Q36 — Completar três letras

Para nomes com menos de três palavras, podemos completar usando letras da última palavra e, se o nome inteiro tiver menos de três letras, completar com X?

Recomendação: sim. Portal Cliente → PCL; Financeiro → FIN; TI → TIX. Para três ou mais palavras, manter iniciais das três primeiras palavras significativas, em maiúsculas sem acento, como RSP e RST; ignorar de/da/do/das/dos/e. Esta é uma proposta de resultado percebido, não uma implementação.

Estado: blocking. Resposta: aguardando.

### Q37 — Outra combinação quando houver colisão

Podemos tentar outras letras do nome, alterando primeiro a terceira posição; se as combinações do nome estiverem ocupadas, usar outras letras de A a Z até encontrar uma sigla livre, sempre com três letras?

Recomendação: sim. Para Rem Soft Projeto Padrão, RSP ocupado pode gerar RSR e depois RSO, usando letras de Projeto. Considerar ocupados também os códigos de projetos arquivados. Se todas as combinações de três letras estiverem ocupadas, informar indisponibilidade e não criar o projeto.

Estado: blocking. Resposta: aguardando.

### Q38 — Estabilidade e edição manual

O identificador deve permanecer somente automático, sem edição manual, e continuar igual quando o projeto for renomeado?

Recomendação: sim, preservando referências. A rejeição em Q31 tratou da resolução de colisões; estas duas propriedades ainda não foram confirmadas separadamente.

Estado: blocking. Resposta: aguardando.

## Respostas Q36–Q38 — 2026-09-10T12:16:36.027828Z

Proveniência: Mário Tinelli, resposta direta na conversa.

### Q36

Resposta literal: q36: concordo

Decisão: Identificador sempre com três letras maiúsculas sem acento. Para três ou mais palavras significativas, iniciais das três primeiras, ignorando de/da/do/das/dos/e. Para menos palavras, completar com letras da última palavra; se faltarem letras no nome inteiro, completar com X. Exemplos: RSP, RST, Portal Cliente → PCL, Financeiro → FIN, TI → TIX.

Estado: resolved.

### Q37

Resposta literal: q37: concordo

Decisão: Colisões usam outras letras do nome, alterando primeiro a terceira posição, como RSP → RSR → RSO. Esgotadas as combinações do nome, usar outras letras A–Z até encontrar sigla livre, sempre com três letras. Códigos de arquivados continuam ocupados. Se todas as combinações estiverem ocupadas, informar indisponibilidade e não criar.

Estado: resolved.

### Q38

Resposta literal: q38: concordo

Decisão: Identificador exclusivamente automático, sem edição manual e imutável após criação, inclusive ao renomear o projeto.

Estado: resolved.

## Auditoria e confirmação do entendimento

Q21–Q38 reconciliadas: criação administrativa, papéis por projeto, identificador automático de três letras e colisões, ausência de datas de projeto, consulta de vínculos, inativação, alteração dos próprios papéis, remoção confirmada com tarefas sem responsável e preservação dos registros anteriores. Retirada de datas limitada aos projetos, sem afetar datas/filtros/indicadores das tarefas. Arquivamento mantém consulta e papéis; bloqueio por cronômetro é integração da Gestão de Tempo. Consulta de projetos e participantes restrita à participação, exceto consulta administrativa de vínculos aprovada. Sem escolha técnica trazida para a entrevista. Nenhum descendente funcional conhecido permanece sem resposta.

Confirmação explícita do entendimento: aguardando usuário. Aprovação do catálogo revisado continua pendente; estados permanecem pausados por essa etapa do fluxo.

## Confirmação explícita do entendimento — 2026-09-10T12:20:18.296259Z

Resposta literal: sim. Mário Tinelli confirmou a síntese integral de Gestão de Projeto e a preparação da revisão do catálogo. Q21–Q38 reconciliadas; aprovação da projeção completa revisada ainda pendente.

## Catálogo revisado aprovado — 2026-09-10T12:23:22.938319Z

Resposta literal: sim. Mário Tinelli aprovou a projeção integral. Pendência resolvida, pausa retomada e entrega reconciliada. Entrevista concluída com entendimento confirmado, sem lacunas funcionais. Requisito completo segue para aprovação.

## Revisão publicada após Gestão de Tempo

Mário Tinelli aprovou o catálogo completo, os quatro documentos e as quatro publicações em etapas explícitas. A descrição de #1014450 foi publicada e relida: status New e relações preservados, sem divergência ou conteúdo externo alterado. Registro da revisão em ../../scopes/2026-09-09-nexum-scope/requirements-time-review.json; operações remotas anteriores preservadas como histórico. Concluído em 2026-09-10T19:09:37.970937Z.

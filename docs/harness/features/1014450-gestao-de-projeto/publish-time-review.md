<!-- project-flow:start -->
## Objetivo

Permitir organizar projetos, participantes e papéis durante seu ciclo de vida pela interface WEB responsiva em português. Administradores criam e administram qualquer projeto, mesmo sem participação; participantes consultam e gestores do projeto mantêm dados, participantes e estado, respeitando as restrições do ciclo de vida.

## Resultado esperado

Um administrador cria um projeto com identificador automático de três letras e gestor principal definido. As pessoas incluídas consultam o projeto conforme seu papel; gestores do projeto e administradores editam, arquivam e reativam. O MVP não apresenta Data inicial nem Prazo do projeto.

## Atores e permissões

- Administrador autenticado e ativo: cria, consulta e administra qualquer projeto, inclusive dados, participantes e arquivamento/reativação, sem exigir participação. O acesso não o inclui automaticamente como participante e respeita estados de somente consulta.
- Participante ativo com papel Membro: consulta projetos dos quais participa e seus dados e participantes.
- Participante ativo com papel Gestor: além da consulta, edita dados, gestor principal, papéis e participantes, arquiva e reativa o projeto.
- Gestor principal: participante Gestor obrigatório, com as mesmas permissões dos demais gestores. Um usuário pode ter papéis diferentes em projetos diferentes.
- Conta inativa: não acessa o sistema, mantendo seus vínculos e papéis registrados.

## Histórias de usuário

1. Como administrador, quero criar um projeto e escolher seu gestor principal para iniciar a organização do trabalho.
2. Como administrador, quero receber um identificador automático, único e estável para reconhecer o projeto.
3. Como participante ou administrador, quero listar e filtrar meus projetos e consultar seus dados e participantes.
4. Como gestor do projeto ou administrador, quero editar dados, participantes e papéis para manter a organização do projeto.
5. Como gestor do projeto ou administrador, quero transferir a responsabilidade principal e alterar meu próprio vínculo com confirmação, preservando a continuidade da gestão.
6. Como gestor do projeto ou administrador, quero arquivar e reativar projetos, mantendo os arquivados disponíveis somente para consulta.
7. Como administrador, quero consultar os projetos e papéis de uma pessoa e acessar o conteúdo dos projetos sem precisar participar.
8. Como gestor do projeto ou administrador, quero preservar vínculos de contas inativas e reconhecer sua situação.
9. Como gestor do projeto ou administrador, quero confirmar a remoção de um participante responsável por tarefas, conhecendo seus efeitos sobre as atribuições.

## Fluxo principal

**Listagem:** apresentar projetos dos quais a pessoa participa, ou todos os projetos para administradores, em cards com identificador, nome, estado e gestor principal. Iniciar com filtro Todos, ordenar alfabeticamente por nome, permitir Todos/Ativos/Arquivados e paginação. Manter o filtro durante a sessão de navegação. Abrir um card leva ao detalhe permitido.

**Criação:** somente o administrador acessa Novo projeto. Informar Nome e Gestor principal obrigatórios, Descrição opcional e participantes ativos com papel Membro ou Gestor. O gestor principal entra obrigatoriamente como Gestor. Gerar identificador automático único de três letras e criar o projeto ativo. O administrador criador só participa quando incluído. Após sucesso, abrir o detalhe se participar; caso contrário, retornar à lista de projetos acessíveis com confirmação.

**Detalhe:** apresentar nome, identificador, descrição, estado, gestor principal e participantes com papéis e indicação de inatividade. Não apresentar datas do projeto. Tarefas, quadro, horas e indicadores ficam disponíveis conforme as Features responsáveis forem entregues e as permissões vigentes.

**Edição:** um gestor do projeto ativo ou administrador altera nome, descrição, principal, participantes e papéis. Ao trocar o principal, o anterior permanece Gestor, salvo alteração explícita de papel ou remoção. O novo principal deve ser ativo e entra como participante Gestor obrigatório. Salvar alterações válidas e apresentar sucesso; cancelar mantém os dados anteriores.

**Próprio acesso:** permitir ao gestor remover a própria participação ou tornar-se Membro, com confirmação e outro gestor principal ativo preservado. Se for o principal, indicar substituto ativo na mesma alteração. Após salvar, aplicar o novo acesso imediatamente; quem saiu e não for administrador não pode continuar no detalhe; quem virou Membro mantém as ações desse papel, além das permissões administrativas se ainda for administrador.

**Arquivamento e reativação:** um gestor do projeto ou administrador confirma o arquivamento. O projeto e seu conteúdo ficam somente para consulta, preservando participantes e papéis. Um gestor do projeto ou administrador pode reativar, restaurando as operações permitidas. A integração da Gestão de Tempo impede arquivar quando houver cronômetro rodando no projeto.

**Consulta administrativa:** na gestão de usuários, abrir Projetos do usuário e mostrar nome, estado e papel em projetos ativos e arquivados. O administrador pode abrir o conteúdo desses projetos mesmo sem participar.

## Fluxos alternativos e exceções

- Nome ou gestor principal ausentes, ou nova seleção de conta inativa: impedir o salvamento e apresentar validação.
- Identificador candidato ocupado: gerar outra combinação automaticamente. Se todas as combinações estiverem ocupadas, informar indisponibilidade e não criar o projeto.
- Pessoa sem participação e sem acesso administrativo tenta consultar projeto, ou sem papel Gestor nem acesso administrativo tenta gerenciá-lo: recusar, inclusive em ação direta ou tela já aberta.
- Projeto arquivado: impedir alterações nos dados e participantes; permitir consulta e reativação pelo gestor do projeto ou administrador.
- Conta desativada: preservar vínculos e papéis e indicar inatividade, sem permitir novas inclusões enquanto inativa. Se todos os gestores estiverem inativos, o administrador pode administrar o projeto e reativar uma dessas contas pela Gestão de Usuário, respeitando as regras do gestor principal.
- Remoção de participante responsável por tarefas: com Gestão de Tarefa disponível, informar o impacto e pedir confirmação. Confirmar remove o vínculo e deixa suas tarefas sem responsável; cancelar preserva vínculo e atribuições. Comentários, horas e histórico anteriores permanecem.
- Nenhum projeto acessível ou nenhum vínculo encontrado: apresentar estado vazio. Falhas apresentam erro e nova tentativa; campos preenchidos permanecem para correção, sem indicar sucesso indevido.

## Regras de negócio

R1. Criação de projetos é exclusiva de administradores ativos. Consulta de conteúdo exige participação ou acesso administrativo; gestão exige papel Gestor no projeto ou acesso administrativo.
R2. Nome e gestor principal são obrigatórios; descrição é opcional. Novo projeto inicia ativo. Data inicial e Prazo do projeto ficam fora do MVP, inclusive exibição e validação; datas das tarefas permanecem nas Features responsáveis.
R3. O principal é participante Gestor obrigatório. Outros gestores têm as mesmas permissões. Criar um projeto não inclui automaticamente o administrador que o criou.
R4. Identificador exclusivamente automático, único e imutável após criar, mesmo ao renomear. Não há edição manual. Deve conter exatamente três letras maiúsculas sem acento.
R5. Usar iniciais das três primeiras palavras significativas, ignorando de/da/do/das/dos/e. Com menos palavras, completar com letras da última palavra; se faltarem letras no nome inteiro, completar com X. Exemplos: Rem Soft Projeto Padrão → RSP; Rem Soft Tool → RST; Portal Cliente → PCL; Financeiro → FIN; TI → TIX.
R6. Em colisão, tentar outras letras do nome, alterando primeiro a terceira posição, como RSP → RSR → RSO. Esgotadas as combinações do nome, usar outras letras A–Z até encontrar uma sigla livre. Códigos de projetos arquivados permanecem reservados. Esgotadas todas as combinações de três letras, informar indisponibilidade sem criar o projeto.
R7. Listagem dos projetos em que participa, ou de todos os projetos para administradores, paginada, em ordem alfabética por nome, com filtro inicial Todos e persistência do filtro durante a sessão.
R8. Trocar o principal inclui o novo como Gestor e mantém o anterior como Gestor, salvo alteração explícita. Remover ou rebaixar o próprio gestor exige confirmação e outro principal ativo; a perda de participação ou privilégio vale imediatamente, preservando o acesso administrativo quando existente.
R9. Inativação de conta preserva vínculos e papéis, mas bloqueia acesso. Contas inativas não podem ser adicionadas a novos vínculos. Reativar uma conta restaura o acesso permitido pelos vínculos e pelo estado do projeto.
R10. Arquivamento exige confirmação e mantém somente consulta; gestores do projeto e administradores podem reativar. O bloqueio por cronômetro rodando será integrado pela Gestão de Tempo.
R11. Consulta administrativa de vínculos inclui projetos ativos e arquivados, nome, estado e papel. O administrador pode acessar o conteúdo independentemente da participação.
R12. A Gestão de Tarefa integra aviso e confirmação para remover participante responsável. A confirmação deixa suas tarefas, inclusive concluídas ou arquivadas, sem responsável, preservando comentários, horas e histórico anteriores. Com Gestão de Tempo, a remoção pausa automaticamente o cronômetro da pessoa e salva o tempo até a alteração, sem finalizar a tarefa.

## Dados percebidos pelo usuário

Nome, identificador automático, descrição, estado Ativo/Arquivado, gestor principal, participantes, papéis Membro/Gestor e indicação de conta inativa. Listagem com filtro e paginação; formulários com validação, salvar e cancelar; confirmações de arquivamento, alteração do próprio acesso e remoção com impacto em tarefas. Modal administrativo com projetos e papéis da pessoa. Sem Data inicial ou Prazo do projeto.

## Critérios de aceite

CA1 — Com administrador ativo, ao criar com nome e principal válidos, gerar projeto ativo com identificador único e incluir o principal como Gestor. Com não administrador, recusar a criação. [R1–R3]
CA2 — Ao criar escolhendo outro principal, incluir o administrador somente se selecionado. Após sucesso, abrir o detalhe se participar; caso contrário, retornar à lista acessível. [R3; criação]
CA3 — Com os nomes de exemplo livres, ao criar, gerar RSP, RST, PCL, FIN e TIX respectivamente, sempre com três letras. [R4–R5]
CA4 — Com sigla ocupada, inclusive por arquivado, ao criar, escolher outra combinação de três letras sem número. Esgotadas as alternativas do nome, usar outra combinação A–Z; esgotadas todas, não criar e informar indisponibilidade. [R6]
CA5 — Ao renomear projeto, manter seu identificador. Tentativas de alterá-lo manualmente são recusadas. [R4]
CA6 — Ao abrir criação, edição, lista ou detalhe, não apresentar datas do projeto. Nome ou principal ausentes e nova inclusão de conta inativa impedem salvar. [R2, R9]
CA7 — Com projetos acessíveis de ambos os estados, ao abrir a lista, mostrar Todos em ordem alfabética, com paginação; ao filtrar e voltar durante a sessão, manter o filtro. Projetos sem participação não aparecem para usuários comuns; administradores podem consultar todos. [R7]
CA8 — Com participante ativo, ao abrir detalhe, apresentar os dados e participantes permitidos. Sem participação e sem acesso administrativo, recusar consulta e operações diretas; administradores acessam qualquer projeto. [R1; detalhe]
CA9 — Com gestor de projeto ativo ou administrador, ao salvar edição válida, persistir e confirmar; ao cancelar, manter os dados anteriores. Membros sem acesso administrativo não podem executar essas alterações. [R1; edição]
CA10 — Ao trocar principal, incluir o novo como Gestor e manter o anterior como Gestor, salvo mudança explícita de papel ou remoção. [R3, R8]
CA11 — Ao confirmar a própria saída ou mudança para Membro com outro principal ativo, salvar e aplicar imediatamente o novo acesso. Sem substituto exigido, recusar; ao cancelar a confirmação, manter o acesso anterior. [R8]
CA12 — Ao desativar participante, preservar vínculo/papel e indicar inatividade, bloqueando acesso e novas inclusões. Ao reativar, permitir acesso conforme os vínculos e o estado do projeto. [R9]
CA13 — Com todos os gestores inativos, após administrador reativar uma dessas contas pela Gestão de Usuário, essa pessoa pode retomar a gestão permitida; o administrador não ganha participação automática. [R1, R9]
CA14 — Ao confirmar arquivamento como gestor, manter projeto e conteúdo somente para consulta. Ao reativar como gestor, restaurar operações permitidas. Membros sem acesso administrativo não podem arquivar ou reativar; administradores podem executar ambas as ações. [R10]
CA15 — Com Gestão de Tempo disponível e cronômetro rodando no projeto, ao tentar arquivar, impedir e informar o motivo. [R10; integração de Gestão de Tempo]
CA16 — Como administrador, ao abrir Projetos do usuário, listar vínculos ativos/arquivados com nome, estado e papel ou estado vazio. Permitir ao administrador acessar o conteúdo mesmo sem participação. [R11]
CA17 — Com Gestão de Tarefa disponível e participante responsável por tarefas, ao remover, informar o impacto e pedir confirmação. Confirmar remove o vínculo e deixa as tarefas sem responsável, preservando os registros anteriores; cancelar mantém vínculo e atribuições. Com Gestão de Tempo e contagem rodando para a pessoa removida, pausar e salvar até a remoção, sem finalizar a tarefa. [R12]
CA18 — Em desktop/mobile, ao usar listas, formulários e diálogos, manter ações utilizáveis por teclado, labels, foco visível e mensagens acessíveis. Falhas permitem nova tentativa e preservam os campos para correção. [Fluxos; guia de design]

## Dependências

Gestão de Usuário (#1014449), com relação nativa 661 já registrada: #1014449 bloqueia #1014450. Gestão de Tarefa entregará tarefas, progresso por quantidade e a integração de remoção confirmada de responsáveis. Gestão de Tempo entregará horas e o bloqueio de arquivamento por cronômetro rodando. Quadro do Projeto e Painel Gerencial fornecem suas navegações e indicadores conforme o catálogo. Esses critérios de integração são verificados quando a capacidade responsável for entregue.

## Dentro do escopo

Criação administrativa, listagem e detalhe por participação ou acesso administrativo, edição por gestor do projeto ou administrador, participantes e papéis, identificador automático, arquivamento/reativação e consulta administrativa de vínculos. Interface WEB em português com cards e formulários responsivos, loading, vazio, erro, indisponibilidade e sucesso. Aplicam-se os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento.

## Fora do escopo

Datas dos projetos, exclusão definitiva de projetos, edição manual de identificadores, participação automática do administrador, subprojetos, Gantt/roadmap, sprints/backlog, dependências entre tarefas, aplicativo nativo e API pública. Datas das tarefas continuam incluídas nas respectivas Features. Implementação de tarefas, horas, cronômetro, quadro e indicadores permanece nas capacidades responsáveis do catálogo.

## Requisito canônico

Documento aprovado: docs/harness/features/1014450-gestao-de-projeto/feature.md

Requisito aprovado por Mário Tinelli.
<!-- project-flow:end -->
# [WEB] [ADMIN] Gestão de Usuário

Issue: #1014449. Versão proposta para aprovação.

## Objetivo

Permitir que administradores mantenham contas, estado e acesso administrativo das pessoas pela interface WEB, com listagem paginada e formulários em modal, preservando as proteções de acesso e a existência de um administrador ativo.

## Resultado esperado

O administrador encontra, cadastra e edita usuários, ativa ou desativa contas e concede ou remove acesso administrativo. A pessoa cadastrada ativa define sua primeira senha por Esqueci minha senha.

## Atores e permissões

Somente administradores autenticados e ativos podem consultar e operar esta gestão. Usuários comuns não podem executar suas ações, inclusive por acesso direto. O acesso administrativo não concede participação automática em projetos.

## Histórias de usuário

1. Como administrador, quero buscar, filtrar e paginar contas para encontrar a pessoa desejada.
2. Como administrador, quero cadastrar nome, e-mail, estado e acesso administrativo para disponibilizar uma conta adequada à pessoa.
3. Como pessoa cadastrada ativa, quero definir minha primeira senha por Esqueci minha senha para acessar o sistema.
4. Como administrador, quero editar os dados e o estado de uma conta para manter seu cadastro e controlar seu acesso.
5. Como administrador, quero conceder ou remover acesso administrativo para controlar quem pode gerir usuários.
6. Como administrador, quero que alterações que eliminem minha própria capacidade administrativa ou o último administrador ativo sejam impedidas para preservar a gestão do sistema.
7. Como administrador, quero receber validação e confirmação das operações em desktop e mobile para corrigir dados e reconhecer o resultado.

## Fluxo principal

**Listagem:** ao acessar Usuários, o administrador encontra contas ativas e inativas, comuns e administrativas, em ordem alfabética por nome. Pode buscar por nome ou e-mail, filtrar por estado e acesso administrativo e navegar pela paginação. A interface apresenta tabela em desktop e cards no mobile.

**Cadastro:** abrir o modal de novo usuário, preencher Nome e E-mail e revisar Estado e Acesso administrativo. Os valores iniciais são Ativo e sem acesso administrativo, podendo ser alterados antes de salvar. Com dados válidos, criar a conta, refletir o resultado na listagem e apresentar sucesso. O cadastro não envia senha nem e-mail adicional automaticamente. A pessoa ativa solicita o link em Esqueci minha senha e define sua senha pelo fluxo já aprovado.

**Edição:** abrir o modal da conta, alterar nome, e-mail, estado ou acesso administrativo e salvar. Com dados válidos e proteções respeitadas, persistir a alteração, atualizar a listagem e apresentar sucesso. O novo e-mail passa a valer imediatamente para login e recuperação, sem confirmação por e-mail, encerramento de sessões ou alteração da senha.

**Controle de acesso:** ativar ou desativar uma conta e conceder ou remover acesso administrativo pela gestão. Remover o privilégio bloqueia as próximas ações administrativas, mantendo as funções comuns enquanto a conta estiver ativa. Desativar bloqueia todo o acesso conforme Autenticação.

## Fluxos alternativos e exceções

- Nome ou e-mail ausentes, e-mail inválido ou usado por outra conta: impedir o salvamento e apresentar validação para correção. Manter o e-mail atual da própria conta editada é permitido.
- Tentativa de autodesativação, remoção do próprio acesso administrativo ou perda do último administrador ativo: recusar a alteração e informar o motivo.
- Acesso por pessoa sem permissão administrativa: recusar consulta e operações. Isso também vale após remoção do privilégio, mesmo com uma tela administrativa já aberta.
- Nenhuma conta encontrada: apresentar estado vazio, distinguindo-o de uma falha de carregamento.
- Falha ao carregar ou salvar: apresentar erro descritivo e permitir nova tentativa, sem indicar sucesso.
- Cancelar o modal não salva as alterações pendentes.

## Regras de negócio

R1. A gestão é exclusiva de administradores autenticados e ativos; a permissão deve valer na consulta e em cada operação.
R2. Nome e e-mail são obrigatórios. O e-mail deve ser válido e único entre as contas, permitindo manter o endereço da conta editada.
R3. O cadastro inicia como Ativo e sem Acesso administrativo; ambas as opções podem ser alteradas antes de salvar.
R4. O primeiro acesso de uma conta ativa usa Esqueci minha senha. O cadastro não envia senha, convite ou e-mail adicional automaticamente.
R5. A listagem abrange contas ativas/inativas e comuns/administrativas, com paginação, busca por nome/e-mail, filtros por estado e acesso administrativo e ordem inicial alfabética por nome.
R6. É proibido desativar a própria conta ou remover o próprio acesso administrativo. Nenhuma alteração pode deixar o sistema sem administrador ativo. Outro administrador pode alterar a conta respeitando essa proteção.
R7. Remover acesso administrativo bloqueia as próximas ações administrativas e mantém o acesso comum da conta ativa. Desativar bloqueia todo o acesso conforme Autenticação.
R8. E-mail alterado vale imediatamente para login e recuperação, sem confirmação por e-mail, encerramento de sessões ou alteração da senha. Se a mesma edição desativar a conta, aplica-se o bloqueio de R7.
R9. Acesso administrativo não concede acesso automático a projetos. Vínculos e sua consulta na tela de usuários pertencem à Gestão de Projeto.

## Dados percebidos pelo usuário

Listagem: Nome, E-mail, Estado, Acesso administrativo, ações da conta, busca, filtros e paginação. Cadastro e edição: Nome, E-mail, Estado e Acesso administrativo, com ações de salvar e cancelar. A interface apresenta carregamento, validação, vazio, erro e sucesso.

## Critérios de aceite

CA1 — Com administrador autenticado e ativo, ao abrir Usuários, apresentar contas de todos os estados e acessos, em ordem alfabética por nome e com paginação. [R1, R5]
CA2 — Com contas cadastradas, ao buscar por nome/e-mail, filtrar por estado/acesso administrativo ou mudar de página, apresentar o conjunto correspondente. Sem resultados, mostrar estado vazio. [R5; fluxos alternativos]
CA3 — Ao abrir o cadastro, apresentar Ativo e Acesso administrativo desmarcado; ao salvar dados válidos, criar a conta com as opções escolhidas e apresentar sucesso. [R2–R3]
CA4 — Ao salvar cadastro ou edição com nome/e-mail ausentes, e-mail inválido ou de outra conta, recusar e apresentar validação. Na edição, aceitar o próprio e-mail atual. [R2]
CA5 — Após cadastrar uma conta ativa, não enviar senha ou e-mail automaticamente; quando a pessoa solicitar Esqueci minha senha, permitir definir a primeira senha pelo fluxo de Recuperação de Senha. [R4]
CA6 — Com dados válidos, ao editar e salvar uma conta, refletir os dados na listagem e apresentar sucesso; ao cancelar, manter os dados anteriores. [Fluxo de edição; fluxos alternativos]
CA7 — Após salvar novo e-mail, ao entrar ou recuperar acesso, usar o novo endereço; o anterior deixa de identificar essa conta. A alteração isolada do e-mail mantém senha e sessões existentes e não exige confirmação por e-mail. [R8]
CA8 — Ao tentar desativar a própria conta, remover o próprio acesso administrativo ou eliminar o último administrador ativo, recusar a alteração e informar o motivo. [R6]
CA9 — Com outro administrador ativo disponível, ao alterar estado ou acesso administrativo de uma conta diferente da própria, permitir a alteração válida respeitando as proteções. [R6]
CA10 — Com conta ativa, ao conceder acesso administrativo, permitir as funções administrativas; ao removê-lo, bloquear a próxima ação administrativa, inclusive em tela já aberta, mantendo as funções comuns. [R1, R7]
CA11 — Ao desativar uma conta, bloquear seu acesso conforme Autenticação; ao reativá-la, permitir autenticação válida conforme seu acesso vigente. [R7]
CA12 — Sem permissão administrativa, ao tentar abrir a gestão ou executar diretamente uma de suas operações, recusar o acesso. Conceder o privilégio não cria participação em projetos. [R1, R9]
CA13 — Em desktop e mobile, ao listar contas e usar os modais, manter tabela/cards, campos e ações utilizáveis por teclado, com labels, foco visível e mensagens acessíveis. Em falha de carregamento ou salvamento, apresentar erro e permitir nova tentativa. [Fluxos; guia de design]

## Dependências

Autenticação, issue #1014446, com relação nativa 660 já registrada: Autenticação bloqueia Gestão de Usuário. O primeiro acesso reutiliza Recuperação de Senha, issue #1014447, já concluída na definição dos requisitos. Gestão de Projeto entregará os vínculos e sua consulta na tela de usuários, conforme o catálogo aprovado.

## Designs e evidências

Fontes design-users e design-guide, decisões Q15–Q20 e confirmação explícita registradas em interview.md. A primeira senha por recuperação substitui o comportamento existente de envio de senha no cadastro. O catálogo atribui a seção de projetos da referência visual à Gestão de Projeto.

## Dentro do escopo

Listagem, busca, filtros, paginação, cadastro, edição, ativação/desativação, concessão/remoção de acesso administrativo e efeitos confirmados. Interface WEB responsiva em português, modais e cards no mobile, com os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento.

## Fora do escopo

Exclusão de contas, envio automático de senha ou convite, definição de senha pelo administrador, confirmação do novo e-mail, manutenção ou consulta de vínculos com projetos nesta entrega, aplicativo nativo e API pública. Meu Perfil e Recuperação de Senha permanecem nas respectivas Features.

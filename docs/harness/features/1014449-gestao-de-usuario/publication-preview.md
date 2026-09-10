<!-- project-flow:start -->
## Objetivo e resultado esperado
Permitir que administradores mantenham contas, estado e acesso administrativo pela interface WEB responsiva em português. A entrega oferece listagem paginada, cadastro e edição em modais, ativação/desativação e concessão/remoção de acesso administrativo, preservando um administrador ativo.

## Atores e permissões
Somente administradores autenticados e ativos podem consultar e operar a gestão, inclusive por acesso direto. A permissão é exigida em cada operação. Acesso administrativo não concede participação automática em projetos.

## Fluxos principais
**Listagem:** apresentar contas ativas/inativas e comuns/administrativas em ordem alfabética por nome, com busca por nome/e-mail, filtros por estado e acesso administrativo e paginação. Usar tabela no desktop e cards no mobile.

**Cadastro:** abrir modal com Nome, E-mail, Estado e Acesso administrativo. Iniciar como Ativo e sem acesso administrativo, permitindo alterar essas opções antes de salvar. Com dados válidos, criar a conta, atualizar a listagem e apresentar sucesso. O cadastro não envia senha, convite ou e-mail adicional automaticamente. A pessoa ativa define sua primeira senha por Esqueci minha senha.

**Edição:** abrir o modal da conta, alterar dados, estado ou acesso administrativo e salvar. Validar os dados e as proteções, persistir, atualizar a listagem e apresentar sucesso. Cancelar não salva alterações pendentes.

**Controle de acesso:** remover acesso administrativo bloqueia as próximas ações administrativas, inclusive em tela já aberta, mantendo as funções comuns da conta ativa. Desativar bloqueia todo o acesso conforme Autenticação; reativar permite autenticação válida conforme o acesso vigente.

## Regras e exceções
- Nome e e-mail obrigatórios; e-mail válido e único entre contas. Manter o próprio endereço da conta editada é permitido.
- Novo e-mail vale imediatamente para login e recuperação, sem confirmação por e-mail, encerramento de sessões ou alteração da senha. Se a mesma edição desativar a conta, o bloqueio de acesso prevalece.
- Proibir autodesativação e remoção do próprio acesso administrativo. Nenhuma alteração pode deixar o sistema sem administrador ativo. Outro administrador pode alterar a conta respeitando essa proteção.
- Dados inválidos ou alterações proibidas impedem o salvamento e apresentam validação ou motivo da recusa.
- Sem resultados, apresentar estado vazio. Falhas de carregamento ou salvamento apresentam erro descritivo e permitem nova tentativa, sem indicar sucesso.

## Critérios de aceite
1. Ao abrir Usuários como administrador autenticado e ativo, apresentar todas as categorias de contas em ordem alfabética por nome e com paginação.
2. Ao buscar, filtrar ou mudar de página, apresentar o conjunto correspondente; sem resultados, mostrar estado vazio.
3. Ao abrir cadastro, apresentar Ativo e Acesso administrativo desmarcado. Ao salvar dados válidos, criar a conta com as opções escolhidas e apresentar sucesso.
4. Nome/e-mail ausentes, e-mail inválido ou de outra conta impedem cadastro e edição, com validação. Aceitar o próprio e-mail atual na edição.
5. Após cadastrar uma conta ativa, não enviar senha ou e-mail automaticamente. Ao solicitar Esqueci minha senha, permitir definir a primeira senha pelo fluxo de Recuperação de Senha.
6. Ao salvar edição válida, refletir os dados na listagem e apresentar sucesso. Ao cancelar, manter os dados anteriores.
7. Após salvar novo e-mail, login e recuperação identificam a conta pelo novo endereço; o anterior deixa de identificá-la. A alteração isolada mantém senha e sessões, sem confirmação por e-mail.
8. Ao tentar autodesativação, remoção do próprio acesso administrativo ou perda do último administrador ativo, recusar a alteração e informar o motivo.
9. Havendo outro administrador ativo, permitir alteração válida de estado ou acesso administrativo de conta diferente da própria, respeitando as proteções.
10. Com conta ativa, conceder acesso administrativo permite as funções administrativas. Removê-lo bloqueia a próxima ação administrativa, inclusive em tela já aberta, mantendo as funções comuns.
11. Desativar bloqueia o acesso conforme Autenticação; reativar permite autenticação válida conforme o acesso vigente.
12. Sem permissão administrativa, recusar consulta e operações diretas. Conceder o privilégio não cria participação em projetos.
13. Em desktop/mobile, tabela/cards e modais são utilizáveis por teclado, com labels, foco visível e mensagens acessíveis. Falhas permitem nova tentativa.

## Dependências e limites
Autenticação (#1014446), com relação 660 existente: #1014446 bloqueia #1014449. O primeiro acesso reutiliza Recuperação de Senha (#1014447). Gestão de Projeto entregará os vínculos e sua consulta na tela de usuários, conforme o catálogo aprovado.

Inclui listagem, busca, filtros, paginação, cadastro, edição, estado, acesso administrativo e efeitos confirmados. Interface em português com modais, cards no mobile, carregamento, validação, vazio, erro e sucesso. Atender ao guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento.

Fora do escopo: exclusão de contas, envio automático de senha ou convite, definição de senha pelo administrador, confirmação do novo e-mail, manutenção ou consulta de vínculos com projetos nesta entrega, aplicativo nativo e API pública. Meu Perfil e Recuperação de Senha permanecem nas respectivas Features.

## Requisito canônico e evidências
Documento aprovado: docs/harness/features/1014449-gestao-de-usuario/feature.md
Evidências: design-users e design-guide. Decisões Q15–Q20 e confirmação em interview.md. A primeira senha por recuperação substitui o envio de senha existente. A seção de projetos da referência visual pertence à Gestão de Projeto. Requisito aprovado por Mário Tinelli.
<!-- project-flow:end -->
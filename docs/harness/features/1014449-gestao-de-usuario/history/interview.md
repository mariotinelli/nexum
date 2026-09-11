# Entrevista — [WEB] [ADMIN] Gestão de Usuário

## Fontes

- [design-users](../../../scopes/2026-09-09-nexum-scope/sources/design-users.md)
- [design-guide](../../../scopes/2026-09-09-nexum-scope/sources/design-guide.md)

## Histórico inicial

Issue #1014449 criada com aprovação de Mário Tinelli. Vínculo #1014446 blocks #1014449 aprovado e criado como relação 660, relido e confirmado sem alterar status New. Aprovação relation-authenticate-users-001 e resultado em relation-operation.json.

## Árvore e fronteira inicial

Q15 primeiro acesso; Q16 autoadministração e preservação de administrador; Q17 valores iniciais; Q18 listagem; Q19 perda de privilégio em sessão; Q20 efeito da edição do e-mail. Perguntas independentes; Q15 pode abrir decisões descendentes sobre convite/primeira senha. Objetivo, exclusividade administrativa, modais, paginação e limites de vínculos com projetos herdados do catálogo. Mecanismos internos não são decisões da entrevista.

## Perguntas e decisões

### Q15 — Primeiro acesso

**Pergunta:** Como a pessoa cadastrada deve definir sua primeira senha?

**Recomendação e justificativa:** Usar o fluxo já aprovado de Esqueci minha senha: após o cadastro ativo, a pessoa solicita o link e define a senha. O cadastro não envia senha nem e-mail adicional automaticamente. O repositório hoje envia uma senha gerada; essa diferença precisa de decisão.

**Resposta:** Aguardando usuário.

**Proveniência:** design-users, design-guide, app/Livewire/Admin/Management/Users/Create.php, Update.php e Index.php; decisões já aprovadas de Autenticação, Recuperação de Senha e Meu Perfil.

**Estado da decisão:** blocking

### Q16 — Alteração do próprio acesso e último administrador

**Pergunta:** Devemos impedir que o administrador desative a própria conta ou remova seu próprio acesso administrativo, e impedir ações que deixem o sistema sem administrador ativo?

**Recomendação e justificativa:** Sim às duas proteções. Outro administrador pode realizar essas alterações, desde que permaneça ao menos um administrador ativo.

**Resposta:** Aguardando usuário.

**Proveniência:** design-users, design-guide, app/Livewire/Admin/Management/Users/Create.php, Update.php e Index.php; decisões já aprovadas de Autenticação, Recuperação de Senha e Meu Perfil.

**Estado da decisão:** blocking

### Q17 — Valores iniciais do cadastro

**Pergunta:** Novas contas devem iniciar como Ativo e sem Acesso administrativo, permitindo ao administrador alterar essas opções antes de salvar?

**Recomendação e justificativa:** Sim, como padrão explícito de criação; conceder acesso administrativo exige marcar a opção.

**Resposta:** Aguardando usuário.

**Proveniência:** design-users, design-guide, app/Livewire/Admin/Management/Users/Create.php, Update.php e Index.php; decisões já aprovadas de Autenticação, Recuperação de Senha e Meu Perfil.

**Estado da decisão:** blocking

### Q18 — Comportamento da listagem

**Pergunta:** A listagem deve incluir contas ativas e inativas, comuns e administrativas, com busca por nome/e-mail e filtros por estado e acesso administrativo?

**Recomendação e justificativa:** Sim; adaptar a busca e os filtros existentes para os dois recortes do Nexum e usar nome em ordem alfabética como ordenação inicial.

**Resposta:** Aguardando usuário.

**Proveniência:** design-users, design-guide, app/Livewire/Admin/Management/Users/Create.php, Update.php e Index.php; decisões já aprovadas de Autenticação, Recuperação de Senha e Meu Perfil.

**Estado da decisão:** blocking

### Q19 — Remoção de acesso administrativo durante o uso

**Pergunta:** Ao remover o acesso administrativo de uma pessoa conectada, devemos bloquear suas próximas ações administrativas e manter seu acesso comum enquanto a conta estiver ativa?

**Recomendação e justificativa:** Sim. Desativação já bloqueia o acesso inteiro na próxima ação; remover apenas o acesso administrativo mantém as funções comuns permitidas.

**Resposta:** Aguardando usuário.

**Proveniência:** design-users, design-guide, app/Livewire/Admin/Management/Users/Create.php, Update.php e Index.php; decisões já aprovadas de Autenticação, Recuperação de Senha e Meu Perfil.

**Estado da decisão:** blocking

### Q20 — Edição do e-mail pelo administrador

**Pergunta:** Quando o administrador salvar um e-mail válido e único, ele deve valer imediatamente para login e recuperação, sem confirmação por e-mail e sem encerrar as sessões existentes?

**Recomendação e justificativa:** Sim, alinhando o efeito da troca de e-mail ao Meu Perfil. A edição não redefine a senha.

**Resposta:** Aguardando usuário.

**Proveniência:** design-users, design-guide, app/Livewire/Admin/Management/Users/Create.php, Update.php e Index.php; decisões já aprovadas de Autenticação, Recuperação de Senha e Meu Perfil.

**Estado da decisão:** blocking

## Reconciliação de evidências

O cadastro atual gera e envia senha; o design mostra nome, e-mail, estado e acesso administrativo sem regra de primeiro acesso. O repositório possui papéis genéricos e filtro de excluídos; o produto define estado e acesso administrativo. Q15 e Q18 confirmam a adaptação observável. Nenhuma recomendação é considerada resposta.

## Entendimento reconciliado

Pendente das respostas.

## Confirmação explícita

Ainda não solicitada.

## Respostas de Q15–Q20 — 2026-09-10T11:33:07.474226Z

### Q15 — resolução

**Resposta literal:** q15: concordo

**Decisão:** Após cadastro ativo, a pessoa define a primeira senha pelo fluxo Esqueci minha senha. Cadastro não envia senha nem e-mail adicional automaticamente.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q16 — resolução

**Resposta literal:** q16: concordo

**Decisão:** Impedir autodesativação e remoção do próprio acesso administrativo. Impedir que o sistema fique sem administrador ativo; outro administrador pode realizar alterações respeitando essa condição.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q17 — resolução

**Resposta literal:** q17: concordo

**Decisão:** Cadastro inicia com estado Ativo e sem Acesso administrativo; administrador pode alterar essas opções antes de salvar.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q18 — resolução

**Resposta literal:** q18: concordo

**Decisão:** Listar todas as contas, ativas/inativas e comuns/administrativas, com busca por nome/e-mail, filtros por estado e acesso administrativo e ordenação inicial alfabética por nome.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q19 — resolução

**Resposta literal:** q19: concordo

**Decisão:** Remover acesso administrativo bloqueia as próximas ações administrativas, mantendo funções comuns enquanto a conta estiver ativa. Desativação bloqueia o acesso inteiro conforme Autenticação.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q20 — resolução

**Resposta literal:** q20: concordo

**Decisão:** Novo e-mail válido e único salvo pelo administrador vale imediatamente para login e recuperação, sem confirmação por e-mail, sem encerrar sessões e sem alterar senha.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

## Auditoria e entendimento para confirmação

Q15–Q20 resolvidas, sem pergunta adiada ou de terceiro. Primeiro acesso usa Recuperação de Senha já concluída; sem convite adicional ou senha enviada automaticamente. A diferença do cadastro existente foi resolvida explicitamente. Público administrador, listagem, cadastro, edição, estado, privilégio e seus efeitos estão definidos. Proteções contra autodesativação e perda do último administrador ativo confirmadas. Modais e interface responsiva/acessível herdados; consulta e manutenção dos vínculos com projetos permanecem na Gestão de Projeto. Nenhuma escolha técnica pendente nesta entrevista.

**Confirmação explícita do entendimento:** Aguardando usuário.

## Confirmação explícita do entendimento — 2026-09-10T11:35:25.136072Z

**Resposta literal:** sim

**Proveniência:** Mário Tinelli, nesta conversa, em resposta à síntese completa. Confirma Q15–Q20, acesso administrativo, modais, paginação e fronteira com Gestão de Projeto. Auditoria concluída sem lacunas, contradições ou questões adiadas. Entrevista concluída; documento completo segue para aprovação.

# Fatiamento de [WEB] [PUBLICO] Autenticação

Revisão: 1  
Hash: `8ffab85e08d4eed826a64f134e57b3e315936fa53278bd073397f59109690bb5`

## Prévia numerada

1. **[DEV] [WEB] [PUBLICO] Autenticação - Entrada e navegação de contas ativas** — 2.5h
   - Entrega: Permitir que pessoas de todos os perfis com conta ativa entrem no Nexum e naveguem pelas capacidades disponíveis e permitidas, em desktop e mobile.
   - Bloqueado por: Nenhum
   - Bloqueios externos: Nenhum
2. **[DEV] [WEB] [PUBLICO] Autenticação - Lembrança e saída por navegador** — 2.5h
   - Entrega: Manter a lembrança de acesso por 30 dias a partir do login e permitir sair apenas do navegador atual.
   - Bloqueado por: Nenhum
   - Bloqueios externos: Nenhum

## Cobertura

| Regra ou critério | Destino | Evidência |
| --- | --- | --- |
| R1: E-mail e senha obrigatórios; somente contas ativas entram. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| R2: Login válido direciona ao painel existente. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| R3: Desativação bloqueia a próxima ação de todas as sessões. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| R4: Lembrança por 30 dias desde o login, sem renovação automática. | Slice 2 | SessionGuard declara 576000 minutos para cookie de lembrança; Logout.php usa logout(), que troca o token compartilhado. Adaptar prazo para 30 dias sem renovação e isolamento de saída, mantendo o bloqueio de conta desativada. |
| R5: Sair encerra apenas o navegador atual e sua lembrança; desativação bloqueia todos. | Slice 2 | SessionGuard declara 576000 minutos para cookie de lembrança; Logout.php usa logout(), que troca o token compartilhado. Adaptar prazo para 30 dias sem renovação e isolamento de saída, mantendo o bloqueio de conta desativada. |
| R6: Cadastro público indisponível, inclusive por rotas diretas. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| R7: Navegação disponibiliza capacidades entregues conforme permissões. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA1: Conta ativa com credenciais válidas acessa o painel. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA2: Ausência de obrigatórios ou e-mail inválido permite corrigir sem autenticar. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA3: Credenciais inválidas e conta inativa são recusadas; inativa recebe orientação de reativação. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA4: Após desativação, a próxima ação é bloqueada em ambos os dispositivos. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA5: Lembrar-me mantém acesso ao reabrir navegador dentro de 30 dias. | Slice 2 | SessionGuard declara 576000 minutos para cookie de lembrança; Logout.php usa logout(), que troca o token compartilhado. Adaptar prazo para 30 dias sem renovação e isolamento de saída, mantendo o bloqueio de conta desativada. |
| CA6: Sem sessão válida após 30 dias, lembrança não autentica; retornos não prorrogam. | Slice 2 | SessionGuard declara 576000 minutos para cookie de lembrança; Logout.php usa logout(), que troca o token compartilhado. Adaptar prazo para 30 dias sem renovação e isolamento de saída, mantendo o bloqueio de conta desativada. |
| CA7: Saída remove sessão e lembrança locais e preserva o outro navegador válido. | Slice 2 | SessionGuard declara 576000 minutos para cookie de lembrança; Logout.php usa logout(), que troca o token compartilhado. Adaptar prazo para 30 dias sem renovação e isolamento de saída, mantendo o bloqueio de conta desativada. |
| CA8: Cadastro público pela interface e rotas não é permitido. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA9: Navegação não concede permissões adicionais de projetos ou administração. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| CA10: Login e navegação utilizáveis em desktop/mobile, por teclado, com labels, foco e retorno acessível. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| ESCOPO-A11Y: Contraste WCAG AA, nomes acessíveis, alvos de toque, hierarquia semântica e redução de movimento. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| ESCOPO-SEG: Senhas protegidas, autorização no servidor e erros sem dados sensíveis. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |
| FLUXO-REC: Entrada para recuperação de acesso acompanha a disponibilidade dessa capacidade; implementação é da Feature própria. | Slice 1 | Login.php restringe perfis e destinos; routes/auth.php expõe cadastro público. Provider Eloquent com SoftDeletes, auth persistente, menus e políticas oferecem base parcial. Views têm labels/erros/loading, mas alternância da senha e navegação exigem completar acessibilidade. A entrega 1 assume as condições integrais deste requisito, incluindo preservação do que já funciona. |

## Descrições completas

### 1. [DEV] [WEB] [PUBLICO] Autenticação - Entrada e navegação de contas ativas

#### Entrega

Permitir que pessoas de todos os perfis com conta ativa entrem no Nexum e naveguem pelas capacidades disponíveis e permitidas, em desktop e mobile.

#### Escopo e limites

Inclui login, painel existente como destino, bloqueio de contas inativas e de sessões após desativação, indisponibilidade do cadastro público e experiência acessível de login/navegação, incluindo os controles Lembrar-me e Sair. Não implementa a administração de contas, recuperação de senha, perfil, projetos ou indicadores. O comportamento temporal da lembrança e o isolamento da saída pertencem à entrega 2.

#### Critérios de aceite

- Conta ativa, de qualquer perfil, com e-mail e senha válidos acessa o painel existente. O login não altera seu perfil nem suas permissões.
- Campos obrigatórios ausentes ou e-mail inválido exibem validação, permitem correção e não autenticam. Credenciais inválidas recusam a entrada; conta inativa é recusada com orientação para solicitar reativação.
- Ao desativar uma conta com sessões abertas em dois dispositivos, a próxima ação autenticada em cada um é bloqueada, inclusive em interações da tela sem navegação completa. A desativação também impede novo login.
- Cadastro público não é disponibilizado nem permite criar contas por acesso direto às rotas públicas existentes. Criação administrativa permanece sob responsabilidade de Gestão de Usuário.
- Navegação exibe somente capacidades entregues e permitidas; autenticar não concede participação em projetos nem acesso administrativo adicional. Restrições são aplicadas no servidor também por acesso direto.
- A entrada para recuperação de acesso fica disponível conforme a capacidade for entregue, sem implementar neste corte o fluxo de recuperação.
- Login e navegação funcionam em desktop e mobile, em português, com campos e controles utilizáveis, labels associados, nomes acessíveis, ordem de teclado e foco visível. Inclui Lembrar-me, revelar senha, menus e Sair.
- A interface atende contraste WCAG AA, hierarquia semântica, alvos de toque adequados e preferência por redução de movimento. Durante o envio apresenta carregamento; erros descritivos e resultado de sucesso são perceptíveis por tecnologias assistivas.
- Senhas permanecem protegidas e não são expostas em mensagens; erros não revelam dados sensíveis. A entrada e a navegação preservam a autorização no servidor.

#### Dependências

Nenhum bloqueio para iniciar: a base de login, contas, autorização e painel já existe. As capacidades das outras Features são disponibilizadas quando entregues, sem antecipar sua implementação.

#### Referências

Item pai Redmine `#1014446`; regras/critérios R1, R2, R3, R6, R7, CA1, CA2, CA3, CA4, CA8, CA9, CA10, ESCOPO-A11Y, ESCOPO-SEG, FLUXO-REC.

### 2. [DEV] [WEB] [PUBLICO] Autenticação - Lembrança e saída por navegador

#### Entrega

Manter a lembrança de acesso por 30 dias a partir do login e permitir sair apenas do navegador atual.

#### Escopo e limites

Inclui prazo fixo da lembrança, retorno após fechar o navegador e saída com remoção de sessão e lembrança locais. Não redefine a validade da sessão ordinária nem implementa recuperação de senha ou administração de contas. Usa o bloqueio de contas desativadas da entrega 1; a experiência acessível dos controles é coberta por ela.

#### Critérios de aceite

- Com conta ativa e Lembrar-me marcado, fechar e reabrir o navegador dentro dos 30 dias do login permite restaurar o acesso.
- Encerrados os 30 dias, a lembrança não autentica. Sem sessão válida, o usuário precisa entrar novamente; acessos intermediários não renovam automaticamente o prazo contado desde o login.
- Com acesso válido em dois navegadores, Sair encerra a sessão e remove a lembrança somente no navegador usado. Retornar nele exige login quando não houver nova sessão válida.
- A saída em um navegador preserva o acesso e a lembrança ainda válidos no outro, inclusive ao fechá-lo e reabri-lo dentro do prazo.
- A lembrança não permite contornar desativação: conta inativa não recupera acesso; a próxima ação de cada sessão da conta desativada é bloqueada, preservando a garantia da entrega 1.

#### Dependências

Nenhum bloqueio para iniciar: o login, a lembrança e a saída já têm base implementada. Coordenar a integração com a entrega 1 para verificar o comportamento completo de contas desativadas; compartilhar código não constitui bloqueio de início.

#### Referências

Item pai Redmine `#1014446`; regras/critérios R4, R5, CA5, CA6, CA7.

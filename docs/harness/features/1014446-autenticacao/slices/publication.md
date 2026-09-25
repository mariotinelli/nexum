# Publicação das filhas de [WEB] [PUBLICO] Autenticação

Item pai Redmine: `1014446`

## Campos nativos aprovados

- Projeto: `65221`
- Pai nativo: `1014446`
- Tracker da mãe: Feature (`2`)
- Tracker DEV: Task (`4`)
- Tracker QA: Deliverable (`5`)
- Status inicial: New (`1`)
- Prioridade inicial: Normal (`4`, regra fixa)
- Categoria herdada: `None`
- Versão herdada: `None`
- Responsável, início e vencimento: vazios

## Campos nativos e descrições

### [DEV] [WEB] [PUBLICO] Autenticação - Entrada e navegação de contas ativas

- Chave interna: `dev-1`
- Tipo: DEV
- Estimativa: 2.5h
- Payload SHA-256: `a7694d03b2ec790ce8a55825027c7846c0e5338ecef0fa628e90b7cb5345de82`

## Entrega

Permitir que pessoas de todos os perfis com conta ativa entrem no Nexum e naveguem pelas capacidades disponíveis e permitidas, em desktop e mobile.

## Escopo e limites

Inclui login, painel existente como destino, bloqueio de contas inativas e de sessões após desativação, indisponibilidade do cadastro público e experiência acessível de login/navegação, incluindo os controles Lembrar-me e Sair. Não implementa a administração de contas, recuperação de senha, perfil, projetos ou indicadores. O comportamento temporal da lembrança e o isolamento da saída pertencem à entrega 2.

## Critérios de aceite

- Conta ativa, de qualquer perfil, com e-mail e senha válidos acessa o painel existente. O login não altera seu perfil nem suas permissões.
- Campos obrigatórios ausentes ou e-mail inválido exibem validação, permitem correção e não autenticam. Credenciais inválidas recusam a entrada; conta inativa é recusada com orientação para solicitar reativação.
- Ao desativar uma conta com sessões abertas em dois dispositivos, a próxima ação autenticada em cada um é bloqueada, inclusive em interações da tela sem navegação completa. A desativação também impede novo login.
- Cadastro público não é disponibilizado nem permite criar contas por acesso direto às rotas públicas existentes. Criação administrativa permanece sob responsabilidade de Gestão de Usuário.
- Navegação exibe somente capacidades entregues e permitidas; autenticar não concede participação em projetos nem acesso administrativo adicional. Restrições são aplicadas no servidor também por acesso direto.
- A entrada para recuperação de acesso fica disponível conforme a capacidade for entregue, sem implementar neste corte o fluxo de recuperação.
- Login e navegação funcionam em desktop e mobile, em português, com campos e controles utilizáveis, labels associados, nomes acessíveis, ordem de teclado e foco visível. Inclui Lembrar-me, revelar senha, menus e Sair.
- A interface atende contraste WCAG AA, hierarquia semântica, alvos de toque adequados e preferência por redução de movimento. Durante o envio apresenta carregamento; erros descritivos e resultado de sucesso são perceptíveis por tecnologias assistivas.
- Senhas permanecem protegidas e não são expostas em mensagens; erros não revelam dados sensíveis. A entrada e a navegação preservam a autorização no servidor.

## Dependências

Nenhum bloqueio para iniciar: a base de login, contas, autorização e painel já existe. As capacidades das outras Features são disponibilizadas quando entregues, sem antecipar sua implementação.

## Referências

Item pai Redmine #1014446; regras/critérios R1, R2, R3, R6, R7, CA1, CA2, CA3, CA4, CA8, CA9, CA10, ESCOPO-A11Y, ESCOPO-SEG, FLUXO-REC.

<!-- project-slices-child:2fcfcd2d0cb3fb290d9709c80750966b29a38cc838734f3cf86738f555f2d534 -->


### [DEV] [WEB] [PUBLICO] Autenticação - Lembrança e saída por navegador

- Chave interna: `dev-2`
- Tipo: DEV
- Estimativa: 2.5h
- Payload SHA-256: `234a37eb204c8f2d56679be07cb5e05327e17136867c1aaa2bc7cf9d854489f2`

## Entrega

Manter a lembrança de acesso por 30 dias a partir do login e permitir sair apenas do navegador atual.

## Escopo e limites

Inclui prazo fixo da lembrança, retorno após fechar o navegador e saída com remoção de sessão e lembrança locais. Não redefine a validade da sessão ordinária nem implementa recuperação de senha ou administração de contas. Usa o bloqueio de contas desativadas da entrega 1; a experiência acessível dos controles é coberta por ela.

## Critérios de aceite

- Com conta ativa e Lembrar-me marcado, fechar e reabrir o navegador dentro dos 30 dias do login permite restaurar o acesso.
- Encerrados os 30 dias, a lembrança não autentica. Sem sessão válida, o usuário precisa entrar novamente; acessos intermediários não renovam automaticamente o prazo contado desde o login.
- Com acesso válido em dois navegadores, Sair encerra a sessão e remove a lembrança somente no navegador usado. Retornar nele exige login quando não houver nova sessão válida.
- A saída em um navegador preserva o acesso e a lembrança ainda válidos no outro, inclusive ao fechá-lo e reabri-lo dentro do prazo.
- A lembrança não permite contornar desativação: conta inativa não recupera acesso; a próxima ação de cada sessão da conta desativada é bloqueada, preservando a garantia da entrega 1.

## Dependências

Nenhum bloqueio para iniciar: o login, a lembrança e a saída já têm base implementada. Coordenar a integração com a entrega 1 para verificar o comportamento completo de contas desativadas; compartilhar código não constitui bloqueio de início.

## Referências

Item pai Redmine #1014446; regras/critérios R4, R5, CA5, CA6, CA7.

<!-- project-slices-child:9144f6ecd5120782d3dd7ce49efc8da616d725e18f47b1d227161eea60b2e61b -->


### [QA] [WEB] [PUBLICO] Autenticação

- Chave interna: `qa`
- Tipo: QA
- Estimativa: 2.5h
- Payload SHA-256: `bb7c711db64c4aa9cfdf98bdaf9b9b9395d1fb1a15870513559d27fe7fd5b7e8`

## Objetivo

Verificar a autenticação completa do Nexum após as duas entregas DEV, incluindo comportamentos reaproveitados, em desktop e mobile.

## Jornadas integradas

- Entrar com conta ativa de cada perfil e credenciais válidas, chegar ao painel existente e navegar somente pelas capacidades entregues e permitidas. Verificar entrada para recuperação conforme sua disponibilidade.
- Enviar formulário com campos obrigatórios ausentes, e-mail inválido e credenciais incorretas: não autenticar, apresentar validação ou erro descritivo e permitir correção. Conta inativa recebe orientação para solicitar reativação.
- Manter duas sessões em dispositivos distintos e desativar a conta: a próxima ação em cada sessão é bloqueada, inclusive nas interações sem navegação completa; novo login e retorno por lembrança também são recusados.
- Entrar com Lembrar-me, fechar e reabrir o navegador dentro dos 30 dias contados desde o login: acesso restaurado. Verificar o término do prazo com avanço controlado do tempo; retornos intermediários não prorrogam a lembrança e, após o prazo sem sessão válida, é exigido novo login.
- Sair em um de dois navegadores: sessão e lembrança locais deixam de autenticar, enquanto o outro mantém sessão e lembrança válidas, inclusive após fechar e reabrir dentro do prazo.
- Em desktop e mobile, percorrer login e navegação por teclado e toque: labels associados, nomes acessíveis, foco visível, ordem de teclado, controles utilizáveis, contraste WCAG AA, alvos de toque adequados, hierarquia semântica e redução de movimento. Incluir revelar senha, Lembrar-me, menus e Sair; carregamento, erros e sucesso devem ser perceptíveis por tecnologias assistivas.

## Regras e permissões

- Cadastro público não permite criar contas pela interface nem por chamadas diretas às rotas públicas existentes.
- Autenticar não altera perfil, não concede participação em projetos nem permissões administrativas. Verificar autorização no servidor por acesso direto, além dos menus.
- Senhas permanecem protegidas e não aparecem nas mensagens; erros não expõem dados sensíveis. Lembrança e sessão ordinária têm validade distinta: o término da lembrança não é motivo para encerrar uma sessão ainda válida.

## Impactos relacionados

- Verificar a preservação do acesso permitido ao painel e da navegação já existente, sem ampliar permissões.
- Recuperação de senha, perfil, gestão de usuários e indicadores permanecem nas respectivas Features; conferir apenas suas entradas já disponíveis neste percurso.
- Preservar a limitação de tentativas, os redirecionamentos permitidos e o acesso às capacidades já existentes durante as adaptações de autenticação.

## Critérios de conclusão

- Todos os cenários de R1–R7 e CA1–CA10 foram executados, incluindo os mecanismos já existentes, com resultado e evidência rastreáveis.
- Registrar navegador, dispositivo ou viewport, perfis utilizados, condições de sessão e lembrança e os instantes usados para verificar os 30 dias sem esperar o prazo real.
- Confirmar os requisitos de segurança e acessibilidade do percurso; registrar divergências e impedimentos explicitamente, sem declarar conformidade de cenários não verificados.

## Referências

Item pai Redmine #1014446; regras/critérios R1, R2, R3, R4, R5, R6, R7, CA1, CA2, CA3, CA4, CA5, CA6, CA7, CA8, CA9, CA10, ESCOPO-A11Y, ESCOPO-SEG, FLUXO-REC.

<!-- project-slices-child:8d052a5a2f84497451084bdfefb5f37c34e1ca8464b097fffe343c948557be3d -->


## Bloqueios nativos

- [DEV] [WEB] [PUBLICO] Autenticação - Entrada e navegação de contas ativas bloqueia [QA] [WEB] [PUBLICO] Autenticação (`blocks`).
- [DEV] [WEB] [PUBLICO] Autenticação - Lembrança e saída por navegador bloqueia [QA] [WEB] [PUBLICO] Autenticação (`blocks`).

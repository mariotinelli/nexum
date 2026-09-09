# [WEB] [PUBLICO] Autenticação

Issue: #1014446. Versão proposta para aprovação.

## Objetivo

Permitir que pessoas com conta ativa entrem e saiam do Nexum, acessando seu ambiente de trabalho por uma interface WEB responsiva em português, conforme suas permissões.

## Resultado esperado

Usuários ativos acessam o painel existente; tentativas inválidas são recusadas com orientação acessível. O usuário pode lembrar o acesso no navegador e encerrá-lo quando desejar.

## Atores e permissões

Pessoas sem sessão e usuários autenticados de todos os perfis. Autenticar não concede acesso administrativo ou participação em projetos. Somente administradores criam contas, pela Feature Gestão de Usuário.

## Histórias de usuário

1. Como pessoa com conta ativa, quero entrar com e-mail e senha para acessar meu trabalho.
2. Como usuário, quero lembrar meu acesso para retornar pelo mesmo navegador sem repetir o login durante o prazo escolhido para o produto.
3. Como usuário, quero sair do navegador atual sem interromper minhas outras sessões.
4. Como administrador, quero que uma conta desativada deixe de acessar a aplicação, inclusive quando já estiver conectada.
5. Como usuário, quero navegar pelas capacidades disponíveis conforme minhas permissões, em desktop ou dispositivo móvel.

## Fluxo principal

1. Abrir o login e informar e-mail e senha.
2. Marcar Lembrar-me quando desejar manter o acesso.
3. Acionar Entrar e receber o estado de carregamento.
4. Com credenciais válidas e conta ativa, acessar o painel existente.
5. Navegar pelas capacidades disponíveis e permitidas.
6. Acionar Sair para encerrar o acesso e remover a lembrança no navegador atual.

## Fluxos alternativos e exceções

- Campos obrigatórios ausentes ou e-mail inválido: apresentar validação e permitir correção.
- Credenciais inválidas: recusar a entrada e apresentar mensagem acessível.
- Conta inativa: impedir a entrada e orientar a solicitar reativação.
- Conta desativada durante o uso: interromper o acesso na próxima ação, em qualquer dispositivo.
- Retorno pelo navegador com Lembrar-me válido: manter o acesso mesmo após fechar e reabrir o navegador.
- Prazo de lembrança encerrado: não restaurar o acesso por essa lembrança; solicitar login quando não houver sessão válida.
- Recuperação de senha: disponibilizar sua entrada conforme a Feature Recuperação de Acesso for entregue.

## Regras de negócio

R1. E-mail e senha são obrigatórios; somente contas ativas podem entrar.
R2. Login válido direciona ao painel existente.
R3. A desativação bloqueia a próxima ação de todas as sessões da conta.
R4. Lembrar-me vale por 30 dias a partir do login, inclusive após fechar o navegador, sem renovação automática do prazo.
R5. Sair encerra somente o acesso do navegador atual e remove sua lembrança. A desativação impede acesso em todos os dispositivos.
R6. Cadastro público fica indisponível, inclusive por acesso direto às rotas existentes.
R7. A navegação respeita permissões e apresenta as capacidades conforme forem entregues.

## Dados percebidos pelo usuário

E-mail, senha, opção Lembrar-me, ações Entrar e Sair, entrada para recuperação de acesso e mensagens de validação, carregamento, erro e sucesso. As mensagens para conta inativa orientam solicitar reativação.

## Critérios de aceite

CA1 — Com conta ativa e credenciais válidas, ao entrar, o usuário acessa o painel existente. [R1–R2]
CA2 — Com campo obrigatório ausente ou e-mail inválido, ao enviar, o formulário informa a validação e permite corrigir sem autenticar. [R1]
CA3 — Com credenciais inválidas ou conta inativa, ao entrar, o acesso é recusado; para conta inativa, há orientação de reativação. [R1]
CA4 — Com sessões abertas em dois dispositivos, ao desativar a conta, a próxima ação em cada um é bloqueada. [R3]
CA5 — Com Lembrar-me marcado e conta ativa, ao fechar e reabrir o navegador dentro dos 30 dias, o acesso é mantido. [R4]
CA6 — Com o prazo de 30 dias encerrado, ao retornar sem sessão válida, a lembrança não autentica; acessos intermediários não prorrogam o prazo. [R4]
CA7 — Com acesso em dois navegadores, ao sair de um, sua sessão e lembrança deixam de permitir acesso; o outro permanece conectado enquanto válido. [R5]
CA8 — Sem autenticação, ao tentar cadastrar uma conta pela interface ou pelas rotas públicas existentes, o cadastro não é permitido. [R6]
CA9 — Com usuário autenticado, ao navegar, somente capacidades entregues e permitidas são disponibilizadas, sem conceder acesso adicional a projetos ou à administração. [R7]
CA10 — Em desktop e mobile, ao preencher e utilizar o login e a navegação, os controles permanecem utilizáveis, com labels, teclado, foco visível e mensagens acessíveis. Durante o envio e seu resultado, há retorno de carregamento e erro ou sucesso. [Fluxo principal; guia de design]

## Dependências

Contas existentes e entrada autenticada do painel existente. Nenhum bloqueador funcional no catálogo aprovado. Os indicadores serão entregues pelo Painel Gerencial; administração de contas e recuperação de acesso são entregas separadas.

## Designs e evidências

Fontes compartilhadas: design-login, design-guide (F01, F02 e RN12), design-profile e design-recover-password. Decisões Q1–Q5 e confirmação do entendimento registradas em interview.md. O repositório evidenciou Lembrar-me e cadastro público existentes; as decisões confirmadas determinam seu comportamento no Nexum.

## Dentro do escopo

Login, lembrança de acesso, bloqueio de contas inativas, saída, redirecionamento, desabilitação do cadastro público e navegação autenticada responsiva. Aplicam-se os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, mensagens descritivas, nomes acessíveis, alvos de toque adequados, hierarquia semântica e redução de movimento. Senhas protegidas, autorização no servidor e erros sem exposição de dados sensíveis.

## Fora do escopo

Recuperação de acesso, manutenção do perfil, gestão de usuários e indicadores gerenciais são Features próprias. Não inclui aplicativo nativo, API pública, importação ou sincronização com Redmine, Jira ou GitLab.

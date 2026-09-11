<!-- project-flow:start -->
# [WEB] [PUBLICO] Autenticação

## Objetivo e resultado esperado
Permitir que pessoas com conta ativa entrem e saiam do Nexum pela interface WEB responsiva em português. Login válido abre o painel existente; tentativas inválidas recebem orientação acessível.

## Atores e permissões
Todos os perfis podem autenticar. O acesso mantém as permissões existentes, sem conceder administração ou participação em projetos. Cadastro público indisponível, inclusive pelas rotas existentes; administradores criam contas pela Gestão de Usuário.

## Fluxo principal
1. Informar e-mail e senha obrigatórios e, opcionalmente, marcar Lembrar-me.
2. Acionar Entrar e acompanhar o carregamento.
3. Com credenciais válidas e conta ativa, acessar o painel existente.
4. Navegar pelas capacidades entregues e permitidas.
5. Acionar Sair para encerrar o acesso no navegador atual.

## Regras e exceções
- Dados obrigatórios ausentes ou e-mail inválido recebem validação e permitem correção.
- Credenciais inválidas impedem a entrada; conta inativa recebe orientação para solicitar reativação.
- Desativar a conta bloqueia a próxima ação em todos os dispositivos.
- Lembrar-me mantém o acesso por 30 dias desde o login, inclusive após fechar o navegador, sem renovar automaticamente o prazo.
- Após esse prazo, a lembrança não restaura o acesso; sem sessão válida, é necessário entrar novamente.
- Sair encerra a sessão e remove a lembrança somente no navegador atual; os demais acessos válidos permanecem.

## Critérios de aceite
1. Credenciais válidas de conta ativa levam ao painel existente.
2. Campos obrigatórios ausentes, e-mail inválido, credenciais inválidas e conta inativa impedem autenticação com retorno acessível; conta inativa recebe orientação de reativação.
3. Ao desativar uma conta conectada em dois dispositivos, a próxima ação em cada um é bloqueada.
4. Com Lembrar-me, fechar e reabrir o navegador dentro dos 30 dias mantém o acesso da conta ativa. Acessos intermediários não prorrogam o prazo; após vencê-lo, a lembrança não autentica sem sessão válida.
5. Ao sair de um navegador, sua sessão e lembrança deixam de permitir acesso; o outro navegador permanece conectado enquanto válido.
6. Tentativas de cadastro público pela interface ou pelas rotas existentes não criam contas.
7. A navegação disponibiliza apenas capacidades entregues e permitidas, sem conceder privilégios adicionais.
8. Login e navegação funcionam em desktop e mobile, com teclado, labels, foco visível e mensagens acessíveis de carregamento, erro ou sucesso.

## Dependências e limites
Utiliza contas existentes e a entrada autenticada do painel existente. Sem bloqueador funcional no catálogo aprovado. Recuperação de acesso, perfil, Gestão de Usuário e indicadores gerenciais pertencem às respectivas Features; suas entradas são disponibilizadas conforme forem entregues.

Inclui autenticação, Lembrar-me, bloqueio de contas inativas, saída, desabilitação do cadastro público e navegação responsiva. Aplicam-se os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, mensagens descritivas, nomes acessíveis, alvos de toque adequados, hierarquia semântica e redução de movimento. Senhas protegidas, autorização no servidor e erros sem exposição de dados sensíveis.

Não inclui aplicativo nativo, API pública, importação ou sincronização com Redmine, Jira ou GitLab.

## Requisito canônico e evidências
Documento aprovado: docs/harness/features/1014446-autenticacao/feature.md
Evidências: design-login, design-guide (F01, F02, RN12), design-profile e design-recover-password. Decisões Q1–Q5 e confirmação do entendimento registradas em interview.md. Requisito aprovado por Mário Tinelli.
<!-- project-flow:end -->
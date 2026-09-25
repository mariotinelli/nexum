# [QA] [WEB] [PUBLICO] Autenticação

- Redmine: `#1014754`
- Tipo: `QA`
- Tracker: Deliverable (`5`)
- Item pai: `#1014446`
- Estimativa: `2.5h`

## Descrição

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

## Relações

- `#1014752` blocks `#1014754`
- `#1014753` blocks `#1014754`

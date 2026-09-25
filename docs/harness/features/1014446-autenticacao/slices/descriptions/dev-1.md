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

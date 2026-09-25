# [QA] [WEB] [PUBLICO] Recuperação de Senha

- Redmine: `#1014815`
- Tipo: `QA`
- Tracker: Deliverable (`5`)
- Item pai: `#1014447`
- Estimativa: `4h`

## Descrição

## Objetivo

Verificar a recuperação de senha completa após as duas entregas DEV, incluindo os comportamentos reaproveitados, em desktop e mobile.

## Jornadas integradas

- Solicitar instruções com e-mail de conta ativa, inexistente e inativa: apresentar a mesma confirmação genérica em todos os casos e enviar o e-mail somente para a conta ativa. Repetir cada solicitação antes de 60 segundos e após o intervalo, registrando o instante controlado e comprovando retorno e espera indistinguíveis, sem novo envio durante a janela.
- Para uma conta ativa, solicitar novamente após 60 segundos e comparar o link anterior com o novo: o anterior não redefine; o novo mantém validade própria de 60 minutos. Verificar também link inválido, expirado e já utilizado, sempre sem alteração da senha e com impedimento acessível.
- Abrir link válido de conta ativa e tentar salvar senhas sem maiúscula, sem minúscula, sem número, sem símbolo, com menos de 8 caracteres, conhecida em vazamentos e com confirmação divergente. Cada condição deve ser recusada e permitir correção; uma senha que cumpra todas as regras deve concluir a redefinição.
- Emitir um link para conta ativa, desativá-la antes do uso e tentar redefinir: impedir a alteração, manter a conta inativa e não conceder acesso ou permissões.
- Preparar sessões e lembranças válidas da mesma conta em múltiplos navegadores ou dispositivos, redefinir a senha com sucesso e tentar reutilizar cada acesso anterior: todos devem ser recusados. Confirmar retorno ao login sem sessão automática, recusa da senha antiga e entrada permitida com a nova senha para a conta ativa.
- Em desktop e mobile, percorrer solicitação, e-mail, redefinição e retorno ao login por teclado e toque. Conferir labels, nomes acessíveis, foco visível, ordem de teclado, revelação de senha, mensagens de carregamento/validação/erro/sucesso, contraste WCAG AA, alvos de toque, hierarquia semântica e preferência por redução de movimento.

## Regras e permissões

- Somente contas ativas recebem instruções e redefinem senha. Recuperação não reativa a conta, não autentica automaticamente e não concede novas permissões.
- A resposta da solicitação e da espera de 60 segundos não revela se o e-mail existe ou se a conta está ativa; chamadas repetidas não disparam novo envio durante a janela.
- Links, senhas e lembranças permanecem protegidos. Mensagens e evidências não expõem token, senha ou outros dados sensíveis.

## Impactos relacionados

- Preservar a entrada compartilhada de recuperação a partir do login e a ação Voltar ao login em toda a jornada, sem mover as rotas para uma área exclusiva de perfil.
- Preservar o envio de e-mail para todos os tipos de usuário com conta ativa e o login posterior conforme as permissões existentes.
- Alteração de senha durante sessão, login comum, cadastro, reativação e administração de contas permanecem fora desta entrega.

## Critérios de conclusão

- Executar todos os cenários de R1–R7 e CA1–CA11, incluindo mecanismos já existentes, com resultado e evidência rastreáveis.
- Registrar e-mail de teste sem dados reais, estado da conta, navegador/dispositivo ou viewport, condições de sessão e lembrança e os instantes controlados usados para verificar 60 segundos e 60 minutos sem esperar os prazos reais.
- Confirmar segurança e acessibilidade do percurso; registrar divergências e impedimentos explicitamente, sem declarar conformidade de cenários não verificados.

## Referências

Item pai Redmine #1014447; regras/critérios R1, R2, R3, R4, R5, R6, R7, CA1, CA2, CA3, CA4, CA5, CA6, CA7, CA8, CA9, CA10, CA11, ESCOPO-A11Y, ESCOPO-SEG.

<!-- project-slices-child:a6cbe090b5f3085b974c6c9f966c7c8fd9ac49a252fb19b010e17f313edab08e -->

## Relações

- `#1014813` blocks `#1014815`
- `#1014814` blocks `#1014815`

# Publicação das filhas de [WEB] [PUBLICO] Recuperação de Senha

Item pai Redmine: `1014447`

## Campos nativos aprovados

- Projeto: `65221`
- Pai nativo: `1014447`
- Tracker da mãe: Feature (`2`)
- Tracker DEV: Task (`4`)
- Tracker QA: Deliverable (`5`)
- Status inicial: New (`1`)
- Prioridade inicial: Normal (`4`, regra fixa)
- Categoria herdada: `None`
- Versão herdada: `None`
- Responsável, início e vencimento: vazios

## Campos nativos e descrições

### [DEV] [WEB] [PUBLICO] Recuperação de Senha - Solicitação segura de instruções

- Chave interna: `dev-1`
- Tipo: DEV
- Estimativa: 3h
- Payload SHA-256: `57aacf934fdf4d0a1a8fade406f42da1bf7dbf94f1623b4ff41e8f0b6724e266`

## Entrega

Ajustar a solicitação existente para enviar instruções somente a contas ativas, mantendo uma resposta indistinguível para qualquer e-mail e aplicando o mesmo intervalo de 60 segundos sem revelar cadastros.

## Escopo e limites

Inclui a tela pública de solicitação, o envio do e-mail com link compartilhado e o ciclo de reenvio. Não inclui a definição da nova senha, a reativação de contas nem uma API pública.

## Critérios de aceite

- Com e-mail válido de conta ativa, a solicitação apresenta confirmação genérica e envia instruções com link para a jornada compartilhada de redefinição.
- Com e-mail inexistente ou de conta inativa, a solicitação apresenta a mesma confirmação genérica, sem enviar instruções e sem revelar a existência ou o estado da conta.
- Sem e-mail ou com formato inválido, o formulário informa a validação, permite correção e não envia instruções.
- Para qualquer e-mail válido, cadastrado ou não, nova solicitação antes de 60 segundos recebe o mesmo retorno e respeita a mesma espera, sem novo envio. Após o intervalo, uma nova solicitação é permitida.
- Em desktop e mobile, a solicitação permanece em português e utilizável por teclado e toque, com label associado, foco visível, nome acessível, alvo adequado, contraste WCAG AA, hierarquia semântica e redução de movimento. Carregamento, validação e confirmação são perceptíveis por tecnologias assistivas, e Voltar ao login permanece disponível.
- O e-mail e as mensagens não expõem senha, token, existência da conta ou outros dados sensíveis.

## Dependências

Nenhum bloqueio para iniciar: o formulário, o broker de senhas, o envio por e-mail e as rotas compartilhadas já existem. A jornada integrada será verificada com a tarefa “Recuperação de Senha - Redefinição e encerramento de acessos”.

## Referências

Item pai Redmine #1014447; regras/critérios R1, R4, CA1, CA2, CA3, CA8.

<!-- project-slices-child:b9565d69990f0aaddfdc758a59beeb3969686c8d6efaced8ee823b366a9f63e4 -->


### [DEV] [WEB] [PUBLICO] Recuperação de Senha - Redefinição e encerramento de acessos

- Chave interna: `dev-2`
- Tipo: DEV
- Estimativa: 4h
- Payload SHA-256: `8f7d8b87c648b3ee9d70bf197a63ca57ee85b132e1c3d8d35c18cf17a858db79`

## Entrega

Completar a redefinição existente para aceitar somente conta ativa e link válido, aplicar integralmente a política de senha e encerrar sessões e lembranças anteriores em todos os dispositivos antes de retornar ao login.

## Escopo e limites

Inclui o formulário público aberto pelo link de recuperação e a invalidação global dos acessos anteriores. Não inclui login automático, alteração de senha durante uma sessão, reativação de contas ou administração de usuários.

## Critérios de aceite

- Com conta ativa e link válido dentro de 60 minutos, uma senha com ao menos 8 caracteres, maiúscula, minúscula, número e símbolo, não conhecida em vazamentos e com confirmação idêntica é salva com sucesso.
- Link inválido, expirado, substituído por novo envio ou já utilizado com sucesso não altera a senha e apresenta o impedimento de forma acessível.
- Se a conta for desativada após a emissão do link, a redefinição é impedida, a conta permanece inativa e nenhuma permissão é concedida.
- Senha que descumpra qualquer regra de composição, seja conhecida em vazamentos ou tenha confirmação diferente é recusada com mensagens que permitem correção sem expor dados sensíveis.
- Após a redefinição bem-sucedida, todas as sessões e lembranças anteriores da conta deixam de permitir acesso em todos os dispositivos; a senha anterior não autentica e a nova autentica a conta ativa.
- O sucesso retorna ao login sem autenticação automática, informa o resultado e mantém Voltar ao login disponível durante a jornada.
- Em desktop e mobile, o formulário permanece em português e utilizável por teclado e toque, com labels associados, revelação de senha acessível, foco visível, nomes acessíveis, alvos adequados, contraste WCAG AA, hierarquia semântica e redução de movimento. Carregamento, validações, impedimentos e sucesso são perceptíveis por tecnologias assistivas.

## Dependências

Nenhum bloqueio para iniciar: token, formulário, política de senha, contas e armazenamento de sessões já existem. Para concluir a jornada de ponta a ponta, integrar com “Recuperação de Senha - Solicitação segura de instruções”; essa integração não impede o início em paralelo.

## Referências

Item pai Redmine #1014447; regras/critérios R2, R3, R5, R6, R7, CA4, CA5, CA6, CA7, CA9, CA10, CA11, ESCOPO-A11Y, ESCOPO-SEG.

<!-- project-slices-child:0495bb4d1f0599e20ae6177bfde04ad7c108faeb5fe14efae277bdb023dbb238 -->


### [QA] [WEB] [PUBLICO] Recuperação de Senha

- Chave interna: `qa`
- Tipo: QA
- Estimativa: 4h
- Payload SHA-256: `7826bdf30cbffd0afe3d77efce8b9af5192894cec5f179b981e9264f5fc97641`

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


## Bloqueios nativos

- [DEV] [WEB] [PUBLICO] Recuperação de Senha - Solicitação segura de instruções bloqueia [QA] [WEB] [PUBLICO] Recuperação de Senha (`blocks`).
- [DEV] [WEB] [PUBLICO] Recuperação de Senha - Redefinição e encerramento de acessos bloqueia [QA] [WEB] [PUBLICO] Recuperação de Senha (`blocks`).

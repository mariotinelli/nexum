# [DEV] [WEB] [PUBLICO] Recuperação de Senha - Redefinição e encerramento de acessos

- Redmine: `#1014814`
- Tipo: `DEV`
- Tracker: Task (`4`)
- Item pai: `#1014447`
- Estimativa: `4h`

## Descrição

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

## Relações

- `#1014814` blocks `#1014815`

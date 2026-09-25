# [DEV] [WEB] [PUBLICO] Recuperação de Senha - Solicitação segura de instruções

- Redmine: `#1014813`
- Tipo: `DEV`
- Tracker: Task (`4`)
- Item pai: `#1014447`
- Estimativa: `3h`

## Descrição

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

## Relações

- `#1014813` blocks `#1014815`

# Fatiamento de [WEB] [PUBLICO] Recuperação de Senha

Revisão: 2  
Hash: `796c9ce94b36727bbc158f86f169f9a1a1b68aa417c52a140a78eda16b31856e`

## Prévia numerada

1. **[DEV] [WEB] [PUBLICO] Recuperação de Senha - Solicitação segura de instruções** — 3h
   - Entrega: Ajustar a solicitação existente para enviar instruções somente a contas ativas, mantendo uma resposta indistinguível para qualquer e-mail e aplicando o mesmo intervalo de 60 segundos sem revelar cadastros.
   - Bloqueado por: Nenhum
   - Bloqueios externos: Nenhum
2. **[DEV] [WEB] [PUBLICO] Recuperação de Senha - Redefinição e encerramento de acessos** — 4h
   - Entrega: Completar a redefinição existente para aceitar somente conta ativa e link válido, aplicar integralmente a política de senha e encerrar sessões e lembranças anteriores em todos os dispositivos antes de retornar ao login.
   - Bloqueado por: Nenhum
   - Bloqueios externos: Nenhum

## Cobertura

| Regra ou critério | Destino | Evidência |
| --- | --- | --- |
| R1: Solicitação exige e-mail válido e não revela se está cadastrado. | Slice 1 | ForgotPassword já valida e mascara usuário inválido; o slice 1 completa a indistinguibilidade durante a espera e preserva o envio somente para conta ativa. |
| R2: Somente contas ativas recebem instruções e redefinem senha; recuperação não reativa. | Slice 2 | SoftDeletes e o provider Eloquent já excluem contas inativas no envio e no reset. O slice 2 assume a garantia integral ao integrar o envio da tarefa “Solicitação segura de instruções” à redefinição, sem reativar a conta. |
| R3: Link vale 60 minutos, permite um sucesso e novo envio invalida o anterior. | Slice 2 | Configuração e repositório já oferecem 60 minutos, um token por e-mail e exclusão após sucesso; o slice 2 assume o ciclo integral desde o link emitido pela tarefa de solicitação até sua utilização ou recusa. |
| R4: Intervalo de 60 segundos por e-mail, com comportamento igual para contas existentes e inexistentes. | Slice 1 | O broker limita apenas usuários encontrados. O slice 1 entrega a mesma janela e o mesmo retorno também para e-mails inexistentes. |
| R5: Senha exige 8 caracteres, maiúscula, minúscula, número, símbolo, não vazada e confirmação idêntica. | Slice 2 | ResetPassword usa a política global correta e confirmação; o slice 2 preserva e comprova todas as condições junto ao fluxo completo. |
| R6: Redefinição encerra todas as sessões e remove Lembrar-me em todos os dispositivos. | Slice 2 | O reset atual troca remember_token, mas não remove sessões persistidas nem usa auth.session. O slice 2 entrega a invalidação global. |
| R7: Sucesso retorna ao login sem autenticação automática. | Slice 2 | ResetPassword já redireciona ao login sem autenticar; o slice 2 preserva o comportamento e torna o resultado acessível. |
| CA1: Conta ativa recebe confirmação genérica e link. | Slice 1 | Envio existente para usuário ativo e URL compartilhada são base parcial; o slice 1 assume o cenário integral. |
| CA2: E-mail inexistente ou conta inativa recebe a mesma confirmação sem envio. | Slice 1 | Usuário ausente ou excluído já não recebe notificação e recebe mensagem genérica; o slice 1 preserva e cobre a conta inativa. |
| CA3: E-mail ausente ou inválido apresenta validação e permite correção. | Slice 1 | Validação requerida e de formato já existe; o slice 1 preserva a correção acessível. |
| CA4: Link válido, conta ativa e senha válida concluem redefinição. | Slice 2 | ResetPassword e o broker já executam o caminho válido; o slice 2 o integra às demais garantias. |
| CA5: Link inválido, expirado ou utilizado impede alteração e informa o impedimento. | Slice 2 | O broker já rejeita token inválido, expirado ou apagado; o slice 2 completa a apresentação acessível do impedimento. |
| CA6: Novo envio invalida o link anterior e inicia validade própria. | Slice 2 | Novo token já substitui o registro anterior; o slice 2 assume a comprovação integrada de que o link substituído é recusado e o novo mantém validade própria. |
| CA7: Conta desativada após emissão não redefine nem é reativada. | Slice 2 | O provider exclui o usuário desativado na validação do reset; o slice 2 preserva e verifica o cenário completo. |
| CA8: Repetição antes de 60 segundos tem a mesma espera e retorno para qualquer e-mail; depois permite nova solicitação. | Slice 1 | A assimetria atual do throttle exige adaptação no slice 1 para qualquer e-mail válido. |
| CA9: Senha fora das regras, vazada ou com confirmação diferente é recusada com validação. | Slice 2 | A política global e confirmed já estão conectados ao reset; o slice 2 preserva mensagens corrigíveis e cobre cada regra. |
| CA10: Sucesso invalida sessões e lembranças, retorna ao login e troca a credencial válida. | Slice 2 | Troca da senha e do remember_token existe, mas sessões anteriores permanecem sem garantia de invalidação; o slice 2 entrega todo o resultado. |
| CA11: Solicitação e redefinição são responsivas, operáveis por teclado e fornecem feedback acessível. | Slice 2 | Layouts e componentes dão base responsiva, de labels, erros e loading; o slice 2 assume a conclusão integrada da acessibilidade nas telas de solicitação e redefinição. |
| ESCOPO-A11Y: Contraste WCAG AA, foco, labels, nomes acessíveis, alvos de toque, semântica e redução de movimento. | Slice 2 | A revelação de senha não é operável por teclado e não houve aferição visual de contraste, toque ou movimento; o slice 2 assume a conformidade integrada de toda a jornada. |
| ESCOPO-SEG: Senhas protegidas e erros sem exposição de dados sensíveis. | Slice 2 | Broker e hash protegem token e senha; o slice 2 assume a garantia integrada de mensagens sem enumeração e ausência de exposição de dados sensíveis. |

## Descrições completas

### 1. [DEV] [WEB] [PUBLICO] Recuperação de Senha - Solicitação segura de instruções

#### Entrega

Ajustar a solicitação existente para enviar instruções somente a contas ativas, mantendo uma resposta indistinguível para qualquer e-mail e aplicando o mesmo intervalo de 60 segundos sem revelar cadastros.

#### Escopo e limites

Inclui a tela pública de solicitação, o envio do e-mail com link compartilhado e o ciclo de reenvio. Não inclui a definição da nova senha, a reativação de contas nem uma API pública.

#### Critérios de aceite

- Com e-mail válido de conta ativa, a solicitação apresenta confirmação genérica e envia instruções com link para a jornada compartilhada de redefinição.
- Com e-mail inexistente ou de conta inativa, a solicitação apresenta a mesma confirmação genérica, sem enviar instruções e sem revelar a existência ou o estado da conta.
- Sem e-mail ou com formato inválido, o formulário informa a validação, permite correção e não envia instruções.
- Para qualquer e-mail válido, cadastrado ou não, nova solicitação antes de 60 segundos recebe o mesmo retorno e respeita a mesma espera, sem novo envio. Após o intervalo, uma nova solicitação é permitida.
- Em desktop e mobile, a solicitação permanece em português e utilizável por teclado e toque, com label associado, foco visível, nome acessível, alvo adequado, contraste WCAG AA, hierarquia semântica e redução de movimento. Carregamento, validação e confirmação são perceptíveis por tecnologias assistivas, e Voltar ao login permanece disponível.
- O e-mail e as mensagens não expõem senha, token, existência da conta ou outros dados sensíveis.

#### Dependências

Nenhum bloqueio para iniciar: o formulário, o broker de senhas, o envio por e-mail e as rotas compartilhadas já existem. A jornada integrada será verificada com a tarefa “Recuperação de Senha - Redefinição e encerramento de acessos”.

#### Referências

Item pai Redmine `#1014447`; regras/critérios R1, R4, CA1, CA2, CA3, CA8.

### 2. [DEV] [WEB] [PUBLICO] Recuperação de Senha - Redefinição e encerramento de acessos

#### Entrega

Completar a redefinição existente para aceitar somente conta ativa e link válido, aplicar integralmente a política de senha e encerrar sessões e lembranças anteriores em todos os dispositivos antes de retornar ao login.

#### Escopo e limites

Inclui o formulário público aberto pelo link de recuperação e a invalidação global dos acessos anteriores. Não inclui login automático, alteração de senha durante uma sessão, reativação de contas ou administração de usuários.

#### Critérios de aceite

- Com conta ativa e link válido dentro de 60 minutos, uma senha com ao menos 8 caracteres, maiúscula, minúscula, número e símbolo, não conhecida em vazamentos e com confirmação idêntica é salva com sucesso.
- Link inválido, expirado, substituído por novo envio ou já utilizado com sucesso não altera a senha e apresenta o impedimento de forma acessível.
- Se a conta for desativada após a emissão do link, a redefinição é impedida, a conta permanece inativa e nenhuma permissão é concedida.
- Senha que descumpra qualquer regra de composição, seja conhecida em vazamentos ou tenha confirmação diferente é recusada com mensagens que permitem correção sem expor dados sensíveis.
- Após a redefinição bem-sucedida, todas as sessões e lembranças anteriores da conta deixam de permitir acesso em todos os dispositivos; a senha anterior não autentica e a nova autentica a conta ativa.
- O sucesso retorna ao login sem autenticação automática, informa o resultado e mantém Voltar ao login disponível durante a jornada.
- Em desktop e mobile, o formulário permanece em português e utilizável por teclado e toque, com labels associados, revelação de senha acessível, foco visível, nomes acessíveis, alvos adequados, contraste WCAG AA, hierarquia semântica e redução de movimento. Carregamento, validações, impedimentos e sucesso são perceptíveis por tecnologias assistivas.

#### Dependências

Nenhum bloqueio para iniciar: token, formulário, política de senha, contas e armazenamento de sessões já existem. Para concluir a jornada de ponta a ponta, integrar com “Recuperação de Senha - Solicitação segura de instruções”; essa integração não impede o início em paralelo.

#### Referências

Item pai Redmine `#1014447`; regras/critérios R2, R3, R5, R6, R7, CA4, CA5, CA6, CA7, CA9, CA10, CA11, ESCOPO-A11Y, ESCOPO-SEG.

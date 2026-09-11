# Entrevista — [WEB] [PUBLICO] Recuperação de Senha

## Fontes

- [design-login](../../../scopes/2026-09-09-nexum-scope/sources/design-login.md)
- [design-recover-password](../../../scopes/2026-09-09-nexum-scope/sources/design-recover-password.md)
- [design-guide](../../../scopes/2026-09-09-nexum-scope/sources/design-guide.md)

## Decisões herdadas

Feature pública WEB responsiva; solicitação por e-mail, resposta que não revela a existência da conta, redefinição com confirmação, rejeição de link inválido ou expirado, retorno ao login. Usuário aprovou a criação com o nome Recuperação de Senha. Issue #1014447 criada e persistida antes da entrevista.

## Árvore e fronteira inicial

Q6 ciclo do link; Q7 estado da conta; Q8 sessões após sucesso; Q9 validação da nova senha; Q10 repetição de solicitações. Todos independentes. Questões descendentes serão recalculadas após as respostas. Objetivo e limites herdados do catálogo; sem escolhas de implementação. Numeração continua após Q1–Q5 da sessão.

## Perguntas e decisões

### Q6 — Validade e uso do link

**Pergunta:** Podemos usar links válidos por 60 minutos, utilizáveis uma única vez, e fazer um novo envio invalidar o link anterior?

**Recomendação e justificativa:** Sim: os 60 minutos já constam no repositório; uso único e prevalência do último link deixam claro qual instrução usar.

**Resposta:** Aguardando usuário.

**Proveniência:** design-recover-password, design-guide, config/auth.php, app/Livewire/Auth/ForgotPassword.php, app/Livewire/Auth/ResetPassword.php e app/Providers/AppServiceProvider.php; leitura do comportamento existente não constitui aprovação do produto.

**Estado da decisão:** blocking

### Q7 — Contas inativas

**Pergunta:** Contas inativas devem receber instruções ou conseguir redefinir a senha por um link recebido antes da desativação?

**Recomendação e justificativa:** Não enviar nem permitir a redefinição enquanto a conta estiver inativa; manter a mesma confirmação genérica na solicitação e nunca reativar a conta pela recuperação.

**Resposta:** Aguardando usuário.

**Proveniência:** design-recover-password, design-guide, config/auth.php, app/Livewire/Auth/ForgotPassword.php, app/Livewire/Auth/ResetPassword.php e app/Providers/AppServiceProvider.php; leitura do comportamento existente não constitui aprovação do produto.

**Estado da decisão:** blocking

### Q8 — Sessões após redefinição

**Pergunta:** Ao redefinir a senha, devemos encerrar as sessões e remover o Lembrar-me em todos os dispositivos?

**Recomendação e justificativa:** Sim; depois, retornar ao login, conforme o fluxo aprovado, exigindo a nova senha.

**Resposta:** Aguardando usuário.

**Proveniência:** design-recover-password, design-guide, config/auth.php, app/Livewire/Auth/ForgotPassword.php, app/Livewire/Auth/ResetPassword.php e app/Providers/AppServiceProvider.php; leitura do comportamento existente não constitui aprovação do produto.

**Estado da decisão:** blocking

### Q9 — Validação da nova senha

**Pergunta:** Mantemos as regras atuais: mínimo de 8 caracteres, maiúscula, minúscula, número, símbolo e rejeição de senhas conhecidas em vazamentos, além da confirmação idêntica?

**Recomendação e justificativa:** Manter as regras existentes evita divergência com os outros fluxos de senha. A política está em app/Providers/AppServiceProvider.php.

**Resposta:** Aguardando usuário.

**Proveniência:** design-recover-password, design-guide, config/auth.php, app/Livewire/Auth/ForgotPassword.php, app/Livewire/Auth/ResetPassword.php e app/Providers/AppServiceProvider.php; leitura do comportamento existente não constitui aprovação do produto.

**Estado da decisão:** blocking

### Q10 — Reenvio das instruções

**Pergunta:** Podemos exigir 60 segundos entre solicitações de recuperação para o mesmo e-mail?

**Recomendação e justificativa:** Sim, seguindo o intervalo existente. Aplicar o mesmo retorno e a mesma espera a e-mails cadastrados e não cadastrados, preservando a confirmação sem revelar a existência da conta.

**Resposta:** Aguardando usuário.

**Proveniência:** design-recover-password, design-guide, config/auth.php, app/Livewire/Auth/ForgotPassword.php, app/Livewire/Auth/ResetPassword.php e app/Providers/AppServiceProvider.php; leitura do comportamento existente não constitui aprovação do produto.

**Estado da decisão:** blocking

## Reconciliação de evidências

Não há nova fonte após decisões desta entrevista. A análise do repositório orienta Q6–Q10; recomendações aguardam confirmação.

## Entendimento reconciliado

Pendente das respostas.

## Confirmação explícita

Ainda não solicitada.

## Respostas da primeira rodada — 2026-09-09T23:19:55.648502Z

### Q6 — resolução

**Resposta literal:** q6: sim

**Decisão:** Link válido por 60 minutos, de uso único; novo envio invalida o link anterior.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. Registro inicial preservado como histórico.

### Q7 — resolução

**Resposta literal:** q7: sim

**Decisão:** Contas inativas não recebem instruções nem podem redefinir a senha, mesmo com link anterior. Solicitação mantém confirmação genérica e não reativa a conta.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. Registro inicial preservado como histórico.

### Q8 — resolução

**Resposta literal:** q8: sim

**Decisão:** Redefinir a senha encerra todas as sessões e remove Lembrar-me de todos os dispositivos. Retorna ao login para autenticar com a nova senha.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. Registro inicial preservado como histórico.

### Q9 — resolução

**Resposta literal:** q9: sim

**Decisão:** Nova senha exige mínimo de 8 caracteres, maiúscula, minúscula, número, símbolo, rejeição de senhas conhecidas em vazamentos e confirmação idêntica.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. Registro inicial preservado como histórico.

### Q10 — resolução

**Resposta literal:** q10: sim

**Decisão:** Intervalo de 60 segundos entre solicitações para o mesmo e-mail, com o mesmo retorno e espera para e-mails cadastrados ou não.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. Registro inicial preservado como histórico.

## Auditoria após Q6–Q10

Objetivo, público, e-mail, resposta genérica, validade e uso do link, estado da conta, validação da nova senha, reenvio e efeito nas sessões possuem evidência ou decisão. Nenhuma pergunta adiada, contradição ou decisão de terceiro pendente. O fluxo termina no login, sem autenticação automática nem reativação de conta. Questões de implementação ficam para o próximo papel. Aprovação documental e publicação permanecem pendentes.

## Entendimento consolidado para confirmação

Solicitar recuperação por e-mail em interface WEB responsiva em português; resposta não revela se a conta existe. Apenas contas ativas recebem instruções e podem redefinir a senha. Link vale por 60 minutos, funciona uma vez e é substituído pelo novo envio; links inválidos, expirados ou já utilizados não permitem redefinir. Reenvio exige 60 segundos, igualmente para e-mails cadastrados ou não. Nova senha segue Q9 e confirmação idêntica. Sucesso encerra todas as sessões e lembranças e retorna ao login. Recuperação não reativa contas. Validações, erros e resultados são acessíveis. Login comum e alteração de senha durante sessão permanecem nas Features próprias.

**Confirmação explícita:** Aguardando usuário.

## Confirmação explícita do entendimento — 2026-09-09T23:20:52.859798Z

Mário Tinelli respondeu **Sim** ao entendimento consolidado após Q6–Q10. Entrevista concluída. Preparação do requisito completo autorizada; aprovação documental e publicação ainda pendentes.

## Aprovação documental — 2026-09-09T23:25:02.054914Z

Mário Tinelli respondeu **aprovado** à íntegra do requisito. SHA-256: `93d1a002be3b3fc0bf30b875525a20ff8f48dd59c37ac0db1da9ef101dd474cc`. Publicação final ainda pendente.

## Correção da publicação — 2026-09-09T23:28:02.701546Z

Mário Tinelli aprovou a descrição e determinou: **mas nao altere o status para approved, nao deve fazer isso**. A publicação contém somente description; status New preservado. A aprovação do requisito não deve mudar status das issues neste fluxo.

## Conclusão — 2026-09-09T23:29:08.674627Z

Descrição aprovada publicada e conferida na issue #1014447, preservando New. Criação, requisito e publicação têm aprovações válidas. Sem relações, divergências, perguntas ou operações pendentes. Fontes e hash canônico conferidos; estado final e transições validados. Próximo papel: planejamento técnico. Nenhuma implementação realizada. Aguardar escolha de continuar ou parar para consolidar o avanço no catálogo.

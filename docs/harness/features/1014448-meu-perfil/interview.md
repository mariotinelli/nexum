# Entrevista — [WEB] [OPERACIONAL] Meu Perfil

## Fontes

- [design-profile](../../scopes/2026-09-09-nexum-scope/sources/design-profile.md)
- [design-guide](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md)

## Histórico inicial

Criação de #1014448 aprovada por Mário Tinelli. Dependência nativa #1014446 blocks #1014448 aprovada separadamente e criada como relação 659; releitura confirmou o vínculo, sem alteração de status. Aprovação relation-authenticate-profile-001 no estado; resultado em relation-operation.json.

## Árvore de decisões

Objetivo, atores e limites herdados: autogestão de nome/e-mail e senha opcional; sem administrar outras contas. Q11 efeito da troca de e-mail; Q12 salvamento conjunto; Q13 validação da senha; Q14 sessões após troca. Fronteira independente. E-mail obrigatório, válido e único já evidenciado; retorno acessível e layout responsivo pertencem ao catálogo. Detalhes de implementação excluídos.

## Perguntas e decisões

### Q11 — Troca de e-mail

**Pergunta:** Ao salvar um novo e-mail válido e não utilizado por outra conta, ele passa a valer imediatamente para login e recuperação, sem confirmação por e-mail?

**Recomendação e justificativa:** Sim, mantendo o comportamento existente. Não há etapa de confirmação no design desta entrega.

**Resposta:** Aguardando usuário.

**Proveniência:** design-profile, design-guide, componentes existentes UpdateProfileInformationForm e UpdatePasswordForm; política aprovada na Feature Recuperação de Senha.

**Estado da decisão:** blocking

### Q12 — Salvar dados e senha

**Pergunta:** Se a pessoa alterar os dados e preencher uma troca de senha inválida, devemos impedir todo o salvamento ou salvar os dados mesmo assim?

**Recomendação e justificativa:** Impedir todo o salvamento, seguindo a ação única Salvar alterações do design. Com os campos de senha vazios, salvar somente nome e e-mail.

**Resposta:** Aguardando usuário.

**Proveniência:** design-profile, design-guide, componentes existentes UpdateProfileInformationForm e UpdatePasswordForm; política aprovada na Feature Recuperação de Senha.

**Estado da decisão:** blocking

### Q13 — Regras da nova senha

**Pergunta:** Aplicamos a mesma política aprovada em Recuperação de Senha: mínimo de 8 caracteres, maiúscula, minúscula, número, símbolo, rejeição de senhas conhecidas em vazamentos e confirmação idêntica?

**Recomendação e justificativa:** Sim. O perfil existente exige apenas 8 caracteres; unificar evita regras diferentes para a mesma senha.

**Resposta:** Aguardando usuário.

**Proveniência:** design-profile, design-guide, componentes existentes UpdateProfileInformationForm e UpdatePasswordForm; política aprovada na Feature Recuperação de Senha.

**Estado da decisão:** blocking

### Q14 — Sessões após trocar a senha

**Pergunta:** A troca de senha pelo perfil deve manter a sessão atual e encerrar as outras sessões e lembranças de acesso, ou exigir novo login em todos os dispositivos?

**Recomendação e justificativa:** Manter a sessão atual e encerrar as demais, removendo Lembrar-me de todos os dispositivos. Aqui a pessoa já está autenticada e confirma a senha atual; pode continuar trabalhando.

**Resposta:** Aguardando usuário.

**Proveniência:** design-profile, design-guide, componentes existentes UpdateProfileInformationForm e UpdatePasswordForm; política aprovada na Feature Recuperação de Senha.

**Estado da decisão:** blocking

## Reconciliação de evidências

O design tem uma ação de salvar; o repositório possui formulários separados. A senha no perfil exige apenas min:8, divergindo da política aprovada em Recuperação de Senha. Q12 e Q13 resolvem o comportamento pretendido.

## Entendimento reconciliado

Pendente das respostas.

## Confirmação explícita

Ainda não solicitada.

## Respostas de Q11–Q14 — 2026-09-10T11:09:58.572552Z

### Q11 — resolução

**Resposta literal:** q11: sim

**Decisão:** Novo e-mail válido e não utilizado passa a valer imediatamente para login e recuperação, sem confirmação por e-mail.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q12 — resolução

**Resposta literal:** q12: dados e troca de senha devem ficar em card separados, cada um com seu componente e botão

**Decisão:** Dados pessoais e troca de senha ficam em cards separados, cada um com seu componente e botão. As ações são independentes; a proposta de salvamento conjunto foi rejeitada.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q13 — resolução

**Resposta literal:** q13: sim

**Decisão:** Aplicar a mesma política de Recuperação de Senha: mínimo de 8 caracteres, maiúscula, minúscula, número, símbolo, rejeição de senhas conhecidas em vazamentos e confirmação idêntica.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q14 — resolução

**Resposta literal:** q14: concordo

**Decisão:** Após trocar a senha, manter a sessão atual, encerrar as demais e remover Lembrar-me de todos os dispositivos.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

## Reconciliação de Q12

A decisão do usuário substitui a ação única do design por dois cards independentes, cada um com seu componente e botão. Salvar dados não solicita nem altera senha; trocar senha não salva alterações pendentes no card de dados. Erros ficam associados à ação correspondente. A composição por componentes é uma orientação explícita do usuário, sem entrevista sobre implementação. A capacidade, os atores e a dependência permanecem iguais.

## Auditoria e entendimento para confirmação

Q11–Q14 resolvidas; sem decisão adiada ou de terceiro. A divergência entre design e comportamento pretendido foi resolvida pelo usuário. Meu Perfil apresenta nome/e-mail no card de dados e senha atual/nova senha/confirmação no card de troca de senha, com botões independentes. Nome e e-mail obrigatórios; e-mail válido e único passa a valer imediatamente. Senha atual correta e nova senha conforme política unificada. Troca mantém a sessão atual, encerra as outras e remove todas as lembranças. Interface responsiva e acessível; somente próprios dados, sem alterar permissões.

**Confirmação explícita do entendimento:** Aguardando usuário.

## Confirmação explícita — 2026-09-10T11:11:57.362027Z

Mário Tinelli respondeu **Sim** ao entendimento consolidado após Q11–Q14. Requisito completo será submetido à aprovação; publicação ainda não autorizada.

## Aprovação documental — 2026-09-10T11:16:01.615708Z

Mário Tinelli respondeu **aprovado** à íntegra do requisito. SHA-256 `63e7c8946c45642ee3c928504dfd6dd8a748eac3953e597cda637616ccd28022`. Publicação da descrição ainda pendente; preservar status.

## Ajuste editorial e aprovação de publicação — 2026-09-10T11:20:28.089283Z

Usuário pediu identificação explícita do card de Dados Pessoais nos fluxos. Prévia dos dois cards apresentada; resposta **O resto está aprovado**. Identificação dos cards ajustada sem mudança de regras; aprovação canônica renovada e publicação da descrição autorizada, preservando New e a relação 659. SHA-256 canônico: `b92d0a6ab0db0364fb4981736c27f880504cc6d1adf694b30638b6124c1f13a9`.

## Conclusão — 2026-09-10T11:21:41.899729Z

Requisito aprovado, descrição ajustada publicada e conferida na issue #1014448. Status New e relação 659 preservados. Estados e transições validados, fontes e hash canônico conferidos, sem gaps ou operações pendentes. Próximo papel recomendado: planejamento técnico. Nenhuma implementação realizada. Aguardar escolha de continuar ou parar para consolidar o avanço no catálogo.

# Entrevista — [WEB] [PUBLICO] Autenticação

## Fontes

- [design-login](../../../scopes/2026-09-09-nexum-scope/sources/design-login.md)
- [design-profile](../../../scopes/2026-09-09-nexum-scope/sources/design-profile.md)
- [design-recover-password](../../../scopes/2026-09-09-nexum-scope/sources/design-recover-password.md)
- [design-guide](../../../scopes/2026-09-09-nexum-scope/sources/design-guide.md)

Catálogo aprovado herdado; issue Redmine #1014446 criada com aprovação explícita de Mário Tinelli.

## Árvore de decisões

Objetivo, login por e-mail e senha, conta ativa, saída, painel e limites: herdados do catálogo aprovado.

Fronteira inicial: Q1 bloqueio de sessão após desativação; Q2 permanência de Lembrar-me; Q3 indisponibilidade de autocadastro. Dependente de Q2: duração e término da lembrança caso mantida. Não solicitar escolhas de implementação. Confirmação do entendimento e aprovação do requisito ainda pendentes.

## Perguntas e decisões

### Q1 — Desativação durante o uso

**Pergunta:** Se uma conta for desativada enquanto a pessoa estiver usando o Nexum, o acesso deve ser interrompido já na próxima ação ou somente no próximo login?

**Recomendação e justificativa:** Interromper na próxima ação, pois a RN12 determina que usuários inativos não podem acessar a aplicação.

**Resposta:** Aguardando usuário.

**Proveniência:** Rodada inicial em 2026-09-09; design-login, design-guide (F01, F02, RN12), routes/auth.php e resources/views/livewire/auth/login.blade.php.

**Estado da decisão:** blocking

### Q2 — Lembrar-me

**Pergunta:** O login do MVP deve manter a opção “Lembrar-me” que existe no repositório, mas não aparece no design aprovado?

**Recomendação e justificativa:** Não oferecer essa opção no MVP, seguindo o formulário do design. Se for mantida, detalharemos sua duração na próxima rodada.

**Resposta:** Aguardando usuário.

**Proveniência:** Rodada inicial em 2026-09-09; design-login, design-guide (F01, F02, RN12), routes/auth.php e resources/views/livewire/auth/login.blade.php.

**Estado da decisão:** blocking

### Q3 — Cadastro público existente

**Pergunta:** As rotas de cadastro público que existem no repositório devem ficar indisponíveis no Nexum, deixando a criação de contas exclusivamente para o administrador?

**Recomendação e justificativa:** Sim. O escopo atribui o cadastro à Gestão de Usuário e não apresenta autocadastro público.

**Resposta:** Aguardando usuário.

**Proveniência:** Rodada inicial em 2026-09-09; design-login, design-guide (F01, F02, RN12), routes/auth.php e resources/views/livewire/auth/login.blade.php.

**Estado da decisão:** blocking

## Reconciliação das evidências

Fontes recebidas e reconciliadas no catálogo, antes da entrevista. O repositório contém Lembrar-me e rotas de cadastro público ausentes do design; Q2 e Q3 resolvem sua aplicação ao produto. Não houve nova fonte após decisões desta entrevista.

## Entendimento reconciliado

Pendente das respostas e da auditoria final.

## Confirmação explícita

Ainda não solicitada.

## Respostas da rodada 1 — 2026-09-09T22:55:14.717202Z

### Q1 — resolução

**Resposta literal:** q1: concordo

**Decisão:** Interromper o acesso de uma conta desativada na próxima ação, inclusive se já estiver autenticada.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. O registro inicial acima permanece como histórico.

### Q2 — resolução

**Resposta literal:** q2: vamos manter nesse MVP

**Decisão:** Manter a opção Lembrar-me neste MVP. Duração e término ainda serão detalhados.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. O registro inicial acima permanece como histórico.

### Q3 — resolução

**Resposta literal:** q3: concordo

**Decisão:** Desabilitar o cadastro público existente; a criação de contas pertence exclusivamente à administração de usuários.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved. O registro inicial acima permanece como histórico.

Q2 mantém o recurso existente apesar de sua ausência no design; a decisão expressa do usuário prevalece. Trata-se de detalhamento da capacidade de autenticação já delimitada, sem nova Feature ou alteração de ordem/dependência.

## Rodada 2 — permanência e saída

### Q4 — Duração de Lembrar-me

**Pergunta:** Por quanto tempo o navegador deve lembrar o acesso após marcar Lembrar-me, inclusive ao fechar e reabrir o navegador?

**Recomendação e justificativa:** Proponho 30 dias a partir do login, sem renovação automática do prazo. É um período explícito para manter a conveniência do acesso recorrente; sair ou desativar a conta interrompe essa lembrança.

**Resposta:** Aguardando usuário.

**Proveniência:** Q2 confirmada por Mário Tinelli; detalhamento funcional da persistência e encerramento do acesso.

**Estado da decisão:** blocking

### Q5 — Alcance de Sair

**Pergunta:** Ao clicar em Sair, devemos encerrar o acesso apenas no navegador atual ou também nos outros dispositivos?

**Recomendação e justificativa:** Somente no navegador atual, removendo também sua lembrança de acesso. Isso permite sair de um dispositivo sem interromper o trabalho em outro; a desativação da conta continua bloqueando todos.

**Resposta:** Aguardando usuário.

**Proveniência:** Q2 confirmada por Mário Tinelli; detalhamento funcional da persistência e encerramento do acesso.

**Estado da decisão:** blocking

**Árvore atual:** Q1–Q3 resolvidas; Q4 e Q5 independentes, abertas. Auditoria e confirmação explícita do entendimento ainda pendentes.

## Respostas da rodada 2 — 2026-09-09T22:56:45.805592Z

### Q4 — resolução

**Resposta literal:** q4: concordo

**Decisão:** Lembrar o acesso por 30 dias a partir do login, inclusive após fechar e reabrir o navegador, sem renovação automática do prazo. Sair ou desativar a conta interrompe a lembrança.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

### Q5 — resolução

**Resposta literal:** q5: concordo

**Decisão:** Sair encerra o acesso somente no navegador atual e remove sua lembrança de acesso. A desativação da conta bloqueia o acesso em todos os dispositivos na próxima ação.

**Proveniência:** Mário Tinelli, resposta direta nesta conversa.

**Estado atual:** resolved.

## Auditoria após Q4 e Q5

Q1–Q5 resolvidas. Objetivo, atores, entradas, navegação, conta inativa, saída, lembrança de acesso e limites possuem evidência ou decisão. Sem questão adiada, conflito de fonte ou dependência de terceiro. A recomendação de omitir Lembrar-me foi substituída pela decisão explícita Q2. Não foram introduzidas escolhas de implementação. O requisito permanece em coleta até a confirmação explícita do entendimento; aprovação do documento e publicação são posteriores.

## Entendimento para confirmação

- Login WEB responsivo, em português, com e-mail e senha obrigatórios, para contas ativas de todos os perfis.
- Credenciais inválidas impedem a entrada; contas inativas recebem orientação para solicitar reativação.
- Login válido abre o painel existente; autenticação não concede participação em projetos nem permissão administrativa.
- Desativação interrompe o acesso na próxima ação em qualquer dispositivo.
- Lembrar-me mantém o acesso no navegador por 30 dias a partir do login, inclusive após fechá-lo, sem renovação automática do prazo.
- Sair encerra o acesso e remove a lembrança apenas no navegador atual; desativar a conta bloqueia todos.
- Cadastro público indisponível; contas são criadas por administradores na Feature Gestão de Usuário.
- Navegação autenticada responsiva respeita permissões e disponibiliza as capacidades conforme forem entregues, com os estados e requisitos de acessibilidade explícitos nas fontes.
- Recuperação de acesso, perfil, gestão de usuários e indicadores gerenciais permanecem nas respectivas Features.

**Confirmação explícita:** Aguardando Mário Tinelli.

## Confirmação explícita do entendimento — 2026-09-09T22:57:46.413921Z

**Resposta literal:** Sim

**Proveniência:** Mário Tinelli, confirmação direta do resumo após Q1–Q5.

Entendimento confirmado e auditoria concluída. Requisito completo preparado para aprovação, sem aprovação de publicação inferida.

## Aprovação do requisito — 2026-09-09T23:04:58.421945Z

Mário Tinelli respondeu **Aprovo** à versão completa apresentada. SHA-256: `27bd56bbf9f72baeca20c4cad1e3319edecc2d6177c5e0992b391dc9c4bf79ca`. Aprovação do documento registrada; publicação final ainda pendente.

## Publicação e conclusão — 2026-09-09T23:08:51.795488Z

Mário Tinelli respondeu **sim** à prévia integral de publicação e alteração para Approved. Aprovação `publish-authenticate-001` registrada antes da atualização. Redmine #1014446 atualizado e relido: descrição aprovada confirmada, Approved (4), nenhum conteúdo externo alterado e nenhuma relação criada.

Validações: requisito canônico mantém o hash aprovado; todas as fontes conferidas; transições e estado final aceitos por validate_state.py. Aprovações de criação, requisito e publicação atribuídas e válidas. Sem gap funcional, divergência ou operação pendente nesta Feature. Nenhum código de aplicação foi implementado. Próximo papel recomendado para este requisito: planejamento técnico da implementação.

A conclusão deste item aguarda apenas a escolha de continuar ou parar para consolidar o avanço no catálogo; o requisito individual está concluído.

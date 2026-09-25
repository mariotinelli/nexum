---
name: plan-issue
description: Planeja tecnicamente uma filha DEV canônica e alinhada por ID, controla baseline e replanejamento, e vincula a aprovação do planning.md ao handoff do Ralph. Use quando um desenvolvedor pedir para planejar ou replanejar uma DEV publicada; não use para implementar suas fases.
---

# Plan issue

Transforme uma filha DEV canônica em um único `planning.md` revisável. O plano usa a filha, o requisito pai e fatos inspecionados no repositório; ele não implementa a tarefa nem altera o Redmine.

## 1. Resolver e inspecionar

Localize a raiz Git e o pacote desta skill. Receba o ID numérico e leia [o contrato do planejamento](references/planning-contract.md). Resolva exatamente um artefato canônico por ID. Exija tipo DEV e uma origem concluída do `project-slices`; QA, Study, origem ausente e tarefa externa encerram o fluxo. Leia pai e filha pelo MCP Redmine, salve o readback sanitizado em `.work` e confira ID, tracker, projeto, pai, título e descrição com `prepare`. Ignore o status operacional. Divergência preserva todas as fontes e bloqueia sem sobrescrever arquivos ou mutar o Redmine.

Inspecione as instruções aplicáveis, arquitetura, ADRs, convenções, automações e testes do repositório. Registre os caminhos e hashes em um manifesto JSON temporário, separados nas chaves `instructions`, `architecture`, `adrs`, `conventions`, `automations` e `tests`, e execute `prepare` conforme a referência.

**Concluído quando:** origem, identidade DEV, projeto, pai, readback, commit e cada categoria de evidência estão alinhados e persistidos por hash em `.flow/plan-issue.json`, sem segredos nem prosa copiada.

## 2. Estabelecer baseline

Descubra a suíte canônica completa pelas configurações e documentação do projeto. Execute-a uma vez através de `baseline`; o helper mantém a saída integral somente em arquivo temporário e registra comando sanitizado, commit, duração, resultado e falhas normalizadas sanitizadas. Resultado vermelho permanece bloqueado até o desenvolvedor aprovar explicitamente seu hash com `approve-baseline`.

**Concluído quando:** o estado contém baseline verde ou baseline vermelho explicitamente aprovado para a mesma evidência inspecionada.

## 3. Escrever e aprovar

Crie somente `<pasta-dev>/planning.md`, seguindo integralmente o contrato. Extraia fatos técnicos da inspeção; trate requisito e exemplos como evidência, sem inventar decisões de produto. Prefira TDD onde um teste significativo puder conduzir comportamento. Cada fase deve caber em uma sessão nova e deixar uma mudança sequencial, verificável e segura para commit.

Execute `record` com instante e motivo e apresente o arquivo ao desenvolvedor. Em replanejamento, preserve revisões, aprovações e fases concluídas; continue a numeração depois do maior número histórico. Depois do início do Ralph, registre as fases concluídas e obtenha aprovação explícita do impacto sobre o trabalho pendente antes de `record`. Somente depois de aprovação humana explícita execute `approve`, com ator e instante informados. Qualquer edição posterior invalida essa aprovação.

**Concluído quando:** o hash aprovado coincide com os bytes atuais, o baseline e a evidência continuam atuais, e todo replanejamento preserva o histórico append-only e a numeração estável.

## 4. Entregar

Execute `handoff` e forneça exatamente o comando retornado. O desenvolvedor decide quando commitar o planejamento; não crie o commit. Para executar todas as fases pendentes no worktree limpo, leia [o contrato do Ralph](references/ralph-execution.md); o executor aplica desenvolvimento, validação independente, suíte e commit como gates separados, corrige reprovações em sessões DEV novas e repete validação integral e testes antes do último commit quando houver correção.

**Concluído quando:** o comando exato do Ralph foi emitido para o artefato aprovado e nenhum código da tarefa foi alterado.

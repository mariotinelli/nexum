---
name: plan-issue
description: Planeja tecnicamente uma tarefa filha DEV em fases executáveis e gera o único planning.md consumido pelo Ralph. Use quando um desenvolvedor pedir o planejamento de uma filha; não use para implementar as fases.
---

# Plan issue

Transforme uma filha DEV em um `planning.md` claro para humanos e executável pelo Ralph. Use `task.md` e o requisito pai como fontes de produto, inspecione o repositório para fatos técnicos e nunca leia ou altere o Redmine.

## 1. Localizar a tarefa

Receba o ID da filha DEV e localize exatamente um `tasks/dev-<id>-<slug>/task.md` em `docs/harness/features` ou `docs/harness/bugs`. Leia também `feature.md` ou `bug.md` do pai. Study e QA não entram neste fluxo.

Leia as instruções aplicáveis do repositório, arquitetura, ADRs, convenções, automações, implementação relacionada e testes existentes. Descubra o comando da suíte completa a partir da configuração real do projeto.

**Concluído quando:** tarefa, requisito pai, padrões relevantes e comando real da suíte foram compreendidos.

## 2. Observar o baseline

Execute a suíte completa uma vez, sem alterar arquivos. Registre no plano o comando exato, se passou e, quando falhar, um resumo sanitizado das falhas. O baseline é contexto para o desenvolvimento; não existe aprovação, hash ou estado separado.

**Concluído quando:** o resultado inicial e suas falhas conhecidas estão descritos no próprio `planning.md`.

## 3. Escrever o planejamento

Leia [o contrato do planejamento](references/planning-contract.md) e crie somente `<pasta-dev>/planning.md`. Garanta que `<pasta-dev>/.gitignore` contenha `/.flow/`; adicione essa linha se estiver ausente. A pasta `.flow` guarda somente a retomada local do Ralph.

Divida o trabalho em fases pequenas e sequenciais. Cada fase deve caber em uma sessão nova, produzir uma mudança verificável e terminar em condição de commit. Escreva para um desenvolvedor humano: explique comportamento, arquivos prováveis, limites, aceite e verificação, sem transformar o plano em uma sequência mecânica de comandos.

Apresente o plano completo ao desenvolvedor e incorpore os ajustes pedidos. O desenvolvedor decide quando commitar o planejamento.

**Concluído quando:** o desenvolvedor revisou o conteúdo, existe exatamente um `planning.md` e todas as fases possuem aceite observável.

## 4. Entregar ao Ralph

Leia [a execução do Ralph](references/ralph-execution.md) e entregue o comando abaixo com o caminho real:

```sh
bash <plan-issue>/ralph.sh execute <pasta-dev>/planning.md
```

Não gere estado, manifesto, readback, aprovação ou hash. O Ralph cria seu estado mínimo automaticamente quando começar.

**Concluído quando:** o comando simples foi informado e nenhum código da tarefa foi implementado.

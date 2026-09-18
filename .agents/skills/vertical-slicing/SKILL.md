---
name: vertical-slicing
description: Evaluate and draft human-readable vertical implementation slices from an approved Feature and inspected code evidence. Use when another planning flow needs behavior-sized DEV work, estimates, real blockers, and exhaustive requirement coverage without publishing tracker issues.
---

# Vertical Slicing

Transforme uma Feature aprovada e evidências de código em entregas DEV estreitas, completas e verificáveis. A disciplina decide a qualidade dos cortes; o fluxo chamador mantém seleção, diálogo, aprovação, persistência e qualquer integração externa.

## Encontrar os cortes

Mapeie cada regra e critério a um comportamento observável. Antes de classificar criação, adaptação ou comportamento existente, leia e aplique [evidência da inspeção](references/inspection-evidence.md). Agrupe mudanças que precisam atravessar juntas as camadas necessárias para produzir o resultado; não crie tarefas por camada e não inclua uma camada que o comportamento não exige.

Integre preparação técnica comum ao primeiro slice que a utiliza. Separe uma preparação apenas quando ela tiver propósito verificável próprio e a exceção ficar explícita para aprovação. Uma Feature pequena pode ser um único slice DEV; comportamento já implementado recebe evidência e cobertura, não trabalho inventado. Quando toda a Feature estiver implementada, proponha slices vazio e cobertura `existing` integral para o fluxo chamador confirmar a decisão por revisão e encaminhar somente a QA.

**Concluído quando:** cada slice entrega um comportamento verificável e todo comportamento da Feature tem exatamente um destino de cobertura.

Compare cada entrega proposta com o significado aprovado do requisito pai. Diferença material não vira slice: devolva ao fluxo chamador o significado aprovado, a correção exata proposta, o impacto e as filhas afetadas. Trate uma API consumível como ampliação material quando ela não aparece no requisito aprovado, ainda que um endpoint pareça tecnicamente conveniente. O fluxo chamador mantém a decisão e o alinhamento do pai.

**Concluído quando:** cada entrega está coberta pelo requisito aprovado ou foi separada como divergência material explícita, sem ampliar o escopo em silêncio.

Quando uma pergunta técnica objetiva impedir a definição dos cortes completos, leia [disciplina de estudos](references/studies.md). Um Study produz evidência para uma proposta posterior; ele não é um slice de comportamento nem autoriza inventar o restante da decomposição.

**Concluído quando:** os cortes completos estão definidos ou a incerteza impeditiva foi formulada como Study limitado.

## Ordenar e estimar

Declare somente bloqueios que impedem iniciar o slice. Para outra Feature, nomeie a capacidade e seu único dono; referencie o slice fornecedor quando ele existir e, enquanto a Feature ainda não tiver filhas, identifique o pai como provisório com motivo explícito. Mantenha a ordem topológica no grafo relevante, não apenas nas arestas propostas; ausência de bloqueio significa início imediato. Estime esforço humano usando agentes. Use seis horas como referência de coesão e contexto, justificando exceções em vez de dividir artificialmente uma entrega.

**Concluído quando:** as arestas são reais e acíclicas, dependências externas não duplicam a capacidade fornecedora, cada estimativa é revisável por uma pessoa e exceções à referência estão explicadas.

## Nomear e descrever

Preserve integralmente o nome e os prefixos da Feature. Prefixe desenvolvimento com `[DEV]` e acrescente o sufixo da entrega. Para uma entrega de API consumível já prevista no requisito, insira `[API]` depois de `[WEB]`, como `[DEV] [WEB] [API] [OPERACIONAL] Gestão de Usuários - Cadastro`; endpoints internos de outro comportamento não recebem o marcador.

Antes de redigir ou revisar descrições, aplique [escrita de tarefas para quem executa](references/task-writing.md). Use os campos existentes para contexto funcional e mudança esperada, limites relevantes, critérios verificáveis, dependências e referências. Contexto técnico permanece opcional e não antecipa a receita de implementação e testes.

Compare cada requisito atribuído ao slice com a descrição completa. Expresse nos critérios as condições observáveis necessárias para verificar a entrega; uma referência em `traceability` não substitui essa explicação. Preserve condições de acessibilidade, responsividade, prazo e permissão quando fizerem parte do requisito, em vez de resumi-las a qualificadores genéricos como “acessível”. Corrija omissões e contradições entre critérios, limites e tabela de cobertura antes de apresentar a proposta.

**Concluído quando:** título e descrição identificam o resultado e seus limites sem depender da conversa nem prescrever o plano técnico, e cada requisito atribuído possui suas condições verificáveis representadas nos critérios.

## Mudanças de requisito

Quando uma nova versão aprovada do requisito suceder a versão usada por um fatiamento publicado, leia [disciplina de mudança semântica](references/semantic-changes.md). Classifique significado, não bytes, e localize afetados e itens ainda válidos antes de qualquer plano de mutação.

**Concluído quando:** a classificação está sustentada pela mudança de comportamento e todo item do baseline foi localizado como afetado ou ainda válido.

Quando a revisão funcional aprovada precisar ser aplicada a tarefas já publicadas, leia [disciplina de aplicação de revisões](references/revision-application.md). Ela define a representação segura por estado da tarefa e a prova final de preservação; o fluxo chamador mantém snapshots, aprovações, persistência e MCP.

**Concluído quando:** cada mudança usa uma representação compatível com o estado remoto atual e nenhuma tarefa concluída ou item fora do impacto foi reescrito.

## Revisar a proposta

Apresente lista numerada com títulos, entregas, estimativas e bloqueios, seguida da tabela de cobertura. Convide o tech lead a unir, dividir e corrigir granularidade ou arestas. Reavalie cobertura e dependências após cada mudança.

Leia [cenários de avaliação](references/evaluation-scenarios.json) ao avaliar a disciplina ou construir regressões semânticas.

**Concluído quando:** nenhuma regra está omitida ou duplicada, nenhuma entrega amplia a Feature e o tech lead considera a granularidade correta.

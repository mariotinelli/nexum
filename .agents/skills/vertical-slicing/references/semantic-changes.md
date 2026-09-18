# Disciplina de mudança semântica

Use esta disciplina quando uma versão aprovada do requisito suceder a versão que fundamentou um fatiamento aprovado. O hash identifica versões; ele não classifica significado. Compare comportamentos observáveis, regras, erros, permissões e limites contra o baseline semântico aprovado.

## Classificar

Classifique como `editorial` quando formatação, ortografia ou redação mudarem sem alterar comportamento, regra, limite ou resultado verificável. Registre cada diferença e explique por que o significado permanece igual. Classifique como `functional` quando ao menos um comportamento observável, regra, limite, critério ou obrigação mudar. Uma diferença de bytes sozinha não sustenta `functional`.

**Concluído quando:** cada diferença relevante possui antes, depois, classificação e justificativa semântica; a classificação geral é `functional` se, e somente se, existir diferença funcional.

## Localizar o impacto

Particione integralmente tarefas publicadas/propostas, critérios de aceite, itens de cobertura e dependências entre afetados e ainda válidos. Para cada item, explique a relação com a mudança. Preserve IDs e evidências dos itens válidos; uma mudança localizada não implica recriar o conjunto inteiro. Inclua decisões sobre filhas adotadas ou externas, resultados de Study, divergências e cobertura de QA entre as evidências preservadas quando existirem.

**Concluído quando:** todo item do baseline aparece exatamente uma vez como afetado ou não afetado e a justificativa permite ao tech lead conferir a fronteira sem conhecer termos internos do agente.

## Vincular a decisão

Apresente classificação e impacto juntos. A aprovação precisa identificar o baseline, a nova versão, a classificação e o plano de impacto exatos. Mudança em qualquer um exige nova decisão. Uma mudança editorial registrada conserva a validade do fatiamento. Uma mudança funcional autoriza somente a preparação de novas revisões para os itens afetados; a política geral de atualizar ou remover tarefas pertence ao fluxo que a implementar.

**Concluído quando:** a decisão atribuída referencia o hash exato da revisão semântica e nenhuma mutação afetada usa aprovação anterior ou mais ampla.

# Entrevista — Painel Gerencial

Issue: #1014550. Responsável pelas decisões: Mário Tinelli.

## Fontes e decisões herdadas

- [Painel](../../../scopes/2026-09-09-nexum-scope/sources/design-dashboard.md), [guia](../../../scopes/2026-09-09-nexum-scope/sources/design-guide.md) e [apontamentos](../../../scopes/2026-09-09-nexum-scope/sources/design-time-entries.md), normalizados no escopo.
- Catálogo aprovado `catalog-time-review-001`, hash `89759a4f2b30efdc34031fcc634de9df05328bbd7704229d7205a02d43d509b0`: membros veem próprias tarefas/horas, gestores veem equipes dos projetos gerenciados e administradores veem todos os projetos.
- Indicadores: projetos ativos, distribuição pelas situações atuais, tarefas atrasadas, finalizadas no período, estimadas versus realizadas, horas por membro e progresso por projeto. Progresso = Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas); conjunto vazio = 0%. Canceladas e Arquivadas não compõem progresso ou atraso.
- Tarefa e Tempo fornecem estados, datas e registros salvos. O painel não produz tarefas ou horas nem altera permissões. Fonte antiga de situações e acesso administrativo é substituída pelos requisitos aprovados.
- A referência contém filtro de finalizações, mas não fecha precisamente os indicadores do membro nem a combinação de papéis. Consulta de Tarefas permite filtros de projeto, situação, prazo, responsável e atraso, mas não possui filtro de data de finalização; Minhas Tarefas possui janela própria de sete dias. Esses limites serão considerados ao definir destinos dos links, sem inventar consultas inexistentes.
- Gestão de Projeto usa ordem alfabética por nome; demais consultas aprovadas usam oito registros por página. São precedentes para apresentação, sem assumir resposta do usuário.
- Relações 669 (#1014465 → #1014550) e 670 (#1014547 → #1014550), ambas blocks, foram aprovadas, criadas sequencialmente e relidas. Status New preservado. Criação e relações não autorizam publicação final.

## Árvore de decisões

Fronteira inicial: combinação de papéis e apresentação do recorte (Q111), projetos considerados (Q112), alcance e período inicial do filtro de finalizações (Q113), paginação de projetos (Q114) e precisão visual do progresso (Q115).

Descendentes: população de tarefas por situação e horas por pessoa, atribuições alteradas e integrantes antigos após definir recortes; seleção de projetos sem tarefas; esforço em Canceladas/Arquivadas; comparação de estimativas com horas; validações e preservação do período após Q113; destinos exatos dos indicadores após Q111–Q113, respeitando as capacidades de consulta já entregues. Se for necessário ampliar consulta ou limites do catálogo, propor revisão antes de alterar essas capacidades. Estados vazios, erros, responsividade e acessibilidade seguem evidência explícita e serão auditados com os cálculos definidos. Excluir escolhas de implementação da entrevista.

## Rodada 1 — aguardando respostas

### Q111 — Papéis diferentes entre projetos

**Pergunta:** Quando a pessoa é gestora em um projeto e membro em outro, o painel deve combinar a equipe do primeiro com apenas suas próprias tarefas e horas do segundo?

**Recomendação:** Sim. Usar os mesmos tipos de indicadores, sempre limitados pelo papel em cada projeto, e identificar esse alcance. Para membros, a seção de horas apresenta somente suas próprias horas; administradores recebem o conjunto de todos os projetos. Nenhum papel de gestão amplia a visão nos projetos em que a pessoa é apenas membro.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q112 — Projetos arquivados

**Pergunta:** Todos os indicadores e a seção de progresso devem considerar somente projetos ativos?

**Recomendação:** Sim, inclusive para administradores. Contar os projetos ativos acessíveis mesmo sem tarefas; apresentar zero nos indicadores sem dados e manter o histórico de projetos arquivados nas consultas existentes. Isso mantém o painel voltado ao trabalho atual.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q113 — Período das finalizações

**Pergunta:** Qual período inicial devemos mostrar e quais indicadores ele deve afetar?

**Recomendação:** Hoje e os 29 dias corridos anteriores, com datas inicial/final inclusivas em Brasília. O filtro altera somente Finalizadas no período; distribuição atual, atrasos, horas, estimativas e progresso não recebem esse corte, seguindo o filtro de finalizações demonstrado na referência.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q114 — Lista de progresso dos projetos

**Pergunta:** Podemos apresentar oito projetos por página, em ordem alfabética pelo nome?

**Recomendação:** Sim. Seguir a ordem da Gestão de Projeto e o tamanho das demais consultas; os indicadores gerais continuam considerando todos os projetos elegíveis, não apenas os da página.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q115 — Percentual de progresso

**Pergunta:** Como devemos apresentar percentuais fracionados de progresso?

**Recomendação:** Arredondar ao inteiro mais próximo: uma de três tarefas finalizada aparece como 33%, duas de três como 67%, mantendo a contagem finalizadas/total ao lado. Sem tarefas elegíveis, mostrar 0%.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

## Confirmação do entendimento

Pendente: a fronteira inicial ainda não foi respondida. Requisito e publicação não aprovados.

## Respostas da rodada 1 — 2026-09-10T20:34:09.707306Z

Proveniência: Mário Tinelli, mensagem desta conversa.

### Resposta Q111

**Resposta literal:** sim

**Entendimento:** Combinar equipes dos projetos gerenciados e próprias tarefas/horas dos projetos como membro; mesmos tipos de indicadores com alcance identificado; administradores recebem todas as equipes.

**Estado:** resolved.

### Resposta Q112

**Resposta literal:** sim

**Entendimento:** Todos os indicadores e progresso consideram somente projetos ativos, inclusive para administradores. Contar projetos ativos acessíveis mesmo sem tarefas e mostrar zero sem dados.

**Estado:** resolved.

### Resposta Q113

**Resposta literal:** pode ser

**Entendimento:** Período inicial: hoje e 29 dias corridos anteriores, datas inclusivas em Brasília. Filtro altera somente Finalizadas no período, sem corte temporal nos demais indicadores.

**Estado:** resolved.

### Resposta Q114

**Resposta literal:** sim

**Entendimento:** Oito projetos por página, em ordem alfabética pelo nome. Indicadores gerais consideram todos os projetos elegíveis, não apenas a página.

**Estado:** resolved.

### Resposta Q115

**Resposta literal:** pode ser

**Entendimento:** Arredondar percentual ao inteiro mais próximo: 1/3=33%, 2/3=67%; manter finalizadas/total ao lado; vazio=0%.

**Estado:** resolved.

## Rodada 2 — aguardando respostas

### Q116 — Situações nos totais

**Pergunta:** Tarefas canceladas e arquivadas devem entrar na distribuição por situação e nos totais de horas estimadas/realizadas?

**Recomendação:** Considerar tarefas não arquivadas, incluindo Canceladas, para distribuição e esforço. O cancelamento não apaga trabalho realizado. Arquivadas ficam fora desses indicadores. Progresso e atraso continuam excluindo ambas, conforme já aprovado. Aplicar sempre o recorte de projetos e pessoas autorizado.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q117 — Horas após troca de responsável

**Pergunta:** Um membro deve continuar vendo suas próprias horas registradas em uma tarefa que passou para outro responsável?

**Recomendação:** Sim, enquanto projeto e tarefa forem elegíveis e o usuário mantiver acesso. Horas seguem quem trabalhou; quantidade de tarefas, estimativa e progresso pessoais seguem a responsabilidade atual. Assim, trocar o responsável não transfere nem esconde as horas de quem trabalhou.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q118 — Pessoas na seção de horas

**Pergunta:** Gestores e administradores devem ver horas de pessoas inativas ou que já saíram do projeto?

**Recomendação:** Sim, quando houver apontamentos elegíveis em nome dessas pessoas. Mostrar também participantes atuais sem horas, com zero. Para o membro, apresentar somente sua própria linha; não expor horas alheias por essa seção.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q119 — Uso do período

**Pergunta:** Podemos exigir as duas datas, impedir início posterior ao fim e preservar o período escolhido durante o acesso atual?

**Recomendação:** Sim. Aplicar ao acionar o filtro; aceitar datas válidas inclusive futuras, que podem resultar em zero. Manter o período ao navegar e recarregar; sair e entrar novamente restaura hoje e os 29 dias anteriores. Erro preserva os valores para correção e não aplica um intervalo inválido.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

### Q120 — Destinos dos links

**Pergunta:** Podemos manter os totais gerais como informativos e oferecer os atalhos detalhados por projeto, além de Minhas Tarefas?

**Recomendação:** Abrir o projeto pelo card; abrir suas tarefas por situação ou atraso na Consulta de Tarefas, com projeto e filtro correspondentes, incluindo responsável atual quando o usuário for apenas membro naquele projeto. A entrada substitui filtros anteriores por esse recorte. Minhas Tarefas abre a visão pessoal existente. Finalizadas no período fica informativo: a consulta atual não possui filtro por data de finalização, e abrir somente Finalizada não reproduziria o resultado exibido. Nenhum total agregado de vários projetos deve abrir uma lista com alcance diferente do indicador.

**Resposta:** Aguardando Mário Tinelli. **Estado:** blocking.

## Fronteira após a rodada 1

Q111–Q115 resolvem composição por papel, projetos ativos, janela inicial, paginação e arredondamento. Q116–Q120 são decisões independentes sobre inclusão por situação, autoria de horas, representação de pessoas, operação do filtro e navegação. Após respostas, auditar comparação de esforço, rótulos do recorte misto, populações de cada indicador e comportamento dos atalhos. A necessidade de filtros de finalização ou seleção composta em consultas existentes somente surgirá se forem solicitados atalhos além dos suportados; nenhuma alteração nessas capacidades foi autorizada.

## Respostas da rodada 2 — 2026-09-10T20:38:09.097242Z

Proveniência: Mário Tinelli, mensagem desta conversa.

### Resposta Q116

**Resposta literal:** pode ser

**Entendimento:** Distribuição por situação e horas estimadas/realizadas incluem Canceladas e excluem Arquivadas. Progresso e atraso excluem ambas; aplicar projetos ativos e recorte autorizado.

**Estado:** resolved.

### Resposta Q117

**Resposta literal:** sim

**Entendimento:** Membro mantém suas próprias horas em tarefa reatribuída enquanto tarefa/projeto forem elegíveis e houver acesso. Horas por pessoa seguem quem trabalhou; tarefas, estimativas e progresso pessoais seguem responsabilidade atual.

**Estado:** resolved.

### Resposta Q118

**Resposta literal:** sim

**Entendimento:** Gestores e administradores veem horas elegíveis de pessoas inativas ou que saíram do projeto. Participantes atuais sem horas aparecem com zero; membro vê somente sua própria linha.

**Estado:** resolved.

### Resposta Q119

**Resposta literal:** sim

**Entendimento:** Exigir ambas as datas, início não posterior ao fim, aplicação pelo botão do filtro e preservação do período até sair da conta. Permitir futuro com eventual zero; novo login restaura hoje e 29 dias anteriores. Erro preserva campos e não aplica intervalo inválido.

**Estado:** resolved.

### Resposta Q120

**Resposta literal:** pode ser

**Entendimento:** Totais gerais informativos; atalhos por projeto para situação ou atraso na Consulta de Tarefas com projeto e responsável pessoal quando aplicável, substituindo filtros anteriores pelo recorte indicado. Link Minhas Tarefas para visão pessoal. Finalizadas no período informativo porque não há filtro de data de finalização na consulta existente.

**Estado:** resolved.

## Auditoria funcional

Q111–Q120 resolvem papéis mistos, universo ativo, período, paginação, cálculo/precisão, situações incluídas, autoria de horas e integrantes antigos, validação/preservação e destinos dos links. Os indicadores usam todos os dados elegíveis, não apenas a página. Quantidades/estimativas/progresso pessoais seguem tarefas atualmente atribuídas; horas pessoais seguem apontamentos da pessoa, inclusive após reatribuição, sem transferir horas. Horas por pessoa são agregadas dentro do alcance de cada projeto; papéis em outro projeto não ampliam acesso. Totais de esforço são somas, incluindo registros salvos e desconsiderando cronômetro ainda não apontado; zero na ausência de dados. Referência demonstra comparação de valores estimados/realizados, sem exigir um novo percentual de desempenho. Dados dos cards, gráficos rotulados, responsividade, vazios/erros e acesso vigente têm evidência ou regra herdada. Os atalhos usam filtros já existentes, sem inventar filtro de data de finalização. Não há lacuna funcional ou pergunta adiada; aguardar confirmação explícita do entendimento consolidado antes do documento completo.

## Entendimento consolidado apresentado

- Considerar somente projetos ativos acessíveis, incluindo os sem tarefas. Administradores veem todos; gestores veem equipes dos projetos gerenciados; membros veem somente suas tarefas e horas. Papéis diferentes são combinados por projeto, com alcance identificado.
- Apresentar projetos ativos, distribuição por situação, atrasadas, finalizadas no período, estimadas versus realizadas, horas por pessoa e progresso por projeto. Indicadores gerais abrangem todo o conjunto elegível, não só os projetos da página.
- Distribuição e esforço incluem Canceladas e excluem Arquivadas. Atraso e progresso excluem ambas. Progresso = Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas), arredondado ao inteiro mais próximo, com contagem ao lado e 0% no vazio.
- Membros mantêm suas próprias horas após reatribuição da tarefa; tarefas, estimativa e progresso pessoais seguem a responsabilidade atual. Horas são de quem trabalhou, limitadas a tarefas/projetos elegíveis e acesso vigente; horas ainda no cronômetro não são apontamento salvo.
- Gestores e administradores veem horas de pessoas inativas ou que saíram, quando há apontamentos elegíveis; participantes atuais sem horas aparecem com zero. Membros veem somente sua própria linha.
- Finalizadas no período inicia com hoje e 29 dias corridos anteriores, datas inclusivas em Brasília. O filtro afeta somente esse indicador. Ambas as datas são obrigatórias, início não pode superar fim, futuro é permitido; aplicar pelo botão. Preservar durante o acesso atual e restaurar padrão no novo login; erros preservam campos para correção.
- Listar oito projetos por página, em ordem alfabética pelo nome, com indicadores e gráficos rotulados, cards e conteúdo empilhado no mobile. Mostrar zero/vazio quando não houver dados e retorno de carregamento, erro e sucesso.
- Totais gerais são informativos. Cards abrem o projeto; atalhos de situação/atraso abrem Consulta de Tarefas com projeto e filtros correspondentes, incluindo responsável pessoal quando aplicável e substituindo filtros anteriores. Minhas Tarefas abre sua visão existente. Finalizadas no período não abre uma consulta que perderia o corte de data.

**Confirmação explícita de Mário Tinelli:** pendente. Documento canônico e publicação ainda não aprovados.

## Confirmação explícita — 2026-09-10T20:39:19.642732Z

Mário Tinelli respondeu **sim** ao entendimento consolidado, decisão understanding-dashboard-001. Entrevista concluída sem lacunas funcionais. Preparar documento completo; aprovação do requisito e publicação permanecem posteriores.

## Documento completo preparado — 2026-09-10T20:42:28.990456Z

feature.md contém todas as seções do contrato, doze histórias, onze regras e 24 critérios de aceite. Revisão cobre Q111–Q120, fórmula de progresso, período exemplificado e populações distintas de responsabilidade/horas; estados válidos. SHA-256 apresentado: `84121a2e81b8516a76b783b1679efbf2dc78ea2b9d65289be0f5031bee9f0019`. Aprovação do documento pendente; nenhuma publicação executada.

## Requisito aprovado e publicação proposta — 2026-09-10T20:43:57.812271Z

Mário Tinelli respondeu **sim** à aprovação do documento completo; requirement-dashboard-001 cobre o SHA-256 `84121a2e81b8516a76b783b1679efbf2dc78ea2b9d65289be0f5031bee9f0019`. Prévia integral em publish-preview.md; argumentos exatos em publish-payload.json, hash `dcf4fb85e34ec616ecd605f94609fe4078578f6071faeb436257ac350ef64bb3`. Releitura confirmou descrição inicial sem divergências, zero bytes externos aos delimitadores, status New e relações 669/670. Proposta altera somente a descrição; publicação aguarda aprovação explícita.

## Publicação concluída — 2026-09-10T20:46:11.399188Z

Mário Tinelli aprovou a prévia integral, aprovação publish-dashboard-001. Descrição publicada e relida: conteúdo aprovado, status New e relações 669/670 preservados. Operação e reconciliação concluídas; requisito válido em completed e sem lacunas funcionais.

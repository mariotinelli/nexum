# [WEB] [OPERACIONAL] Painel Gerencial

Issue: #1014550.

## Objetivo

Permitir que usuários ativos acompanhem progresso, atrasos e esforço dos projetos pela interface WEB em português, com indicadores limitados pelo papel exercido em cada projeto. O painel agrega tarefas e apontamentos existentes, identifica o alcance dos dados e oferece navegação para projetos e consultas correspondentes.

## Resultado esperado

Consultar a situação atual dos projetos ativos, o trabalho finalizado no período e os totais estimados e realizados, sem expor dados além do recorte autorizado. Gestores acompanham suas equipes, membros acompanham suas responsabilidades e horas, e administradores acompanham todos os projetos ativos. Os indicadores gerais abrangem todo o conjunto elegível, independentemente da paginação dos projetos.

## Atores e permissões

Todos os acessos exigem conta autenticada e ativa. Definir o alcance separadamente para cada projeto ativo:

| Papel no projeto | Tarefas, estimativas e progresso | Horas realizadas |
| --- | --- | --- |
| Membro | Tarefas atualmente atribuídas ao próprio usuário | Apontamentos do próprio usuário, inclusive em tarefas reatribuídas |
| Gestor | Tarefas de toda a equipe do projeto gerenciado | Apontamentos de toda a equipe, inclusive pessoas inativas ou removidas |
| Administrador | Tarefas de qualquer projeto, mesmo sem participação | Apontamentos de qualquer projeto, mesmo sem participação |

Combinar os recortes quando a pessoa tem papéis diferentes: gestor em A e membro em B vê a equipe de A e somente suas tarefas e horas de B. A gestão de A não amplia sua visão em B. Administradores recebem o alcance administrativo completo. Identificar os recortes pessoal e de equipe para que os valores sejam compreensíveis.

Projetos arquivados ficam fora de todos os indicadores e da lista de progresso, inclusive para administradores. Contar projetos ativos acessíveis mesmo sem tarefas. Revalidar acesso vigente em consultas e destinos de navegação; perda de participação sem alcance administrativo ou inativação impede acesso indevido.

## Histórias de usuário

1. Como usuário, quero consultar indicadores conforme meu papel em cada projeto para acompanhar somente os dados permitidos.
2. Como gestor em alguns projetos e membro em outros, quero combinar esses recortes sem ampliar permissões.
3. Como usuário, quero ver quantos projetos ativos estão acessíveis, inclusive os ainda sem tarefas.
4. Como usuário, quero consultar a distribuição por situação e os atrasos para compreender o trabalho atual.
5. Como usuário, quero escolher um período de finalizações para acompanhar entregas realizadas nessas datas.
6. Como usuário, quero comparar totais estimados e realizados dentro do meu alcance para acompanhar esforço.
7. Como membro, quero manter a visibilidade das horas que trabalhei após uma troca de responsável.
8. Como gestor ou administrador, quero consultar horas por pessoa, preservando o trabalho de quem ficou inativo ou saiu do projeto.
9. Como usuário, quero ver o progresso de cada projeto e sua contagem de tarefas elegíveis.
10. Como usuário, quero percorrer projetos paginados sem reduzir os totais gerais do painel.
11. Como usuário, quero abrir projetos e consultas com o recorte correspondente para examinar os dados apresentados.
12. Como usuário, quero compreender gráficos, valores vazios e mensagens de falha em desktop e mobile.

## Fluxo principal

**Entrada:** abrir o Painel Gerencial pela navegação autenticada existente. Determinar os projetos ativos acessíveis e o papel em cada um. Apresentar projetos ativos, distribuição de tarefas por situação, tarefas atrasadas, Finalizadas no período, horas estimadas versus realizadas, horas por pessoa e progresso dos projetos. Sem período preservado, usar hoje e os 29 dias corridos anteriores.

**População de tarefas:** em cada projeto, considerar todas as tarefas não arquivadas no recorte de equipe ou somente as atualmente atribuídas ao usuário no recorte pessoal. A distribuição inclui Pendente, Em andamento, Pausada, Finalizada e Cancelada. Arquivadas ficam fora. Aplicar esse conjunto às estimativas; cancelamento não remove a tarefa da distribuição ou do esforço.

**População de horas:** considerar apontamentos salvos de tarefas não arquivadas nos projetos ativos elegíveis. No recorte de equipe, somar os registros de todas as pessoas; no recorte pessoal, somente os registros da própria pessoa, mesmo se a tarefa estiver atualmente atribuída a outro responsável. Registros de tarefas Canceladas permanecem elegíveis; registros de Arquivadas ou de projetos arquivados ficam fora. A perda de acesso ao projeto retira os dados do painel daquela pessoa, sem apagar o histórico existente.

**Projetos ativos:** contar cada projeto ativo acessível uma vez, mesmo sem tarefas ou sem tarefas pessoais. Não restringir a contagem aos oito projetos da página atual. Projetos sem dados no recorte apresentam valores zero.

**Atrasos e situação:** apresentar contagens por situação no recorte de tarefas. Atraso exige prazo anterior a hoje e situação Pendente, Em andamento ou Pausada, conforme Gestão de Tarefa. Finalizadas, Canceladas, Arquivadas e tarefas sem prazo não são atrasadas. Prazo de hoje ou futuro não caracteriza atraso.

**Finalizações:** usar a data de finalização, e não o prazo da tarefa, para contar Finalizadas entre as datas inicial e final, inclusive, no horário de Brasília. Exigir ambas as datas e início não posterior ao fim; permitir datas futuras. O usuário altera as datas e aciona o botão do filtro. O período afeta somente Finalizadas no período; não corta distribuição atual, atrasos, estimativas, horas ou progresso. Preservar o período ao navegar e recarregar durante o acesso atual. Novo login restaura hoje e os 29 dias anteriores.

**Esforço:** apresentar os valores totais de horas estimadas e realizadas, respeitando suas populações. Estimativas pessoais são das tarefas atualmente atribuídas; realizadas pessoais são de quem trabalhou. Após reatribuição, esses valores podem refletir conjuntos diferentes, sem transferir horas para o novo responsável. Identificar esse alcance; não tratar horas registradas por terceiros como horas próprias. Tempo apenas em contagem no cronômetro ainda não é apontamento salvo. Ausência de valores contribui com zero; horas realizadas podem superar estimativas, sem reduzir os valores apresentados.

**Horas por pessoa:** agregar os apontamentos elegíveis por sua pessoa original. Gestores e administradores veem pessoas inativas ou removidas que tenham registros elegíveis e participantes atuais sem horas com zero. Em projetos onde o usuário é apenas membro, contribuir somente com sua própria linha. Ao combinar projetos, somar por pessoa apenas as contribuições autorizadas de cada projeto, sem duplicar os registros.

**Progresso:** calcular por projeto, dentro do recorte de tarefas, `Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas) × 100`. Canceladas e Arquivadas não entram no numerador ou denominador. Denominador zero resulta em 0%. Exibir percentual arredondado ao inteiro mais próximo e a contagem finalizadas/total ao lado: 1/3 corresponde a 33%; 2/3, a 67%. O período de finalizações não altera o progresso atual.

**Lista de projetos:** apresentar oito projetos por página, em ordem alfabética pelo nome, com controles de paginação. Cards identificam projeto, identificador, estado ativo, gestor, prazo, contagem finalizadas/total, percentual e horas realizadas conforme o recorte permitido. Os indicadores gerais continuam considerando todos os projetos elegíveis. Gráficos e valores têm rótulos; no mobile, indicadores, gráficos e cards ficam empilhados.

**Navegação:** totais gerais são informativos. O card abre o projeto autorizado. Atalhos por projeto de situação ou atraso abrem Consulta de Tarefas com o projeto e o filtro correspondente; quando a pessoa é apenas membro naquele projeto, incluir o próprio responsável como filtro. A entrada substitui os filtros anteriores por esse recorte, evitando interferência de outra consulta. Para gestor ou administrador, usar o conjunto da equipe daquele projeto. O link Minhas Tarefas abre a visão pessoal existente, com suas regras próprias. Finalizadas no período não tem atalho para uma consulta que perderia o corte de data; a consulta atual não possui filtro por data de finalização.

Os filtros iniciais dos atalhos representam o indicador de origem. Após entrar na Consulta de Tarefas, continuam valendo suas permissões e operações já aprovadas; o painel não transforma o filtro pessoal em uma nova restrição geral de acesso a tarefas.

## Fluxos alternativos e exceções

- Sem projetos ativos acessíveis: mostrar vazio e indicadores zero, sem expor dados de projetos arquivados ou não autorizados.
- Projeto ativo sem tarefas elegíveis: contar o projeto, mostrar contagens e horas aplicáveis ao recorte, com progresso 0% quando não houver tarefas no denominador.
- Somente Canceladas: distribuição e esforço podem ter valores; atraso e progresso são zero.
- Datas ausentes, inválidas ou início posterior ao fim: não aplicar o intervalo, informar o erro e preservar os campos para correção.
- Período sem finalizações ou inteiramente futuro sem correspondências: mostrar zero, mantendo os demais indicadores sem corte temporal.
- Tarefa reatribuída: tarefas, estimativa e progresso pessoais acompanham o responsável atual; horas permanecem atribuídas a quem trabalhou, enquanto elegíveis.
- Pessoa inativada ou removida do projeto: registros elegíveis continuam compondo os indicadores da equipe autorizada, sem conceder acesso à pessoa removida ou inativa.
- Projeto arquivado ou tarefa arquivada: deixar de compor os conjuntos definidos, preservando consulta histórica nas capacidades existentes.
- Acesso ou papel mudou: recalcular o recorte autorizado em nova consulta e revalidar o destino de um link; não manter acesso por existir uma tela aberta.
- Falha ou indisponibilidade: mostrar mensagem e permitir nova tentativa com o período preservado, sem apresentar falha como resultado zero válido ou como sucesso.

## Regras de negócio

R1. Somente conta ativa consulta o painel. O conjunto contém projetos ativos acessíveis, inclusive sem tarefas; administradores veem todos. Papéis são aplicados por projeto, sem propagação de privilégios entre eles.

R2. Tarefas, estimativas e progresso usam o recorte da equipe para gestor/administrador e a responsabilidade atual para membro. Distribuição e esforço incluem Canceladas e excluem Arquivadas; todos os conjuntos excluem projetos arquivados.

R3. Horas são somas de apontamentos salvos, limitados por projeto e situação elegíveis. Membro vê somente horas registradas por si, independentemente da responsabilidade atual da tarefa. Gestor/administrador vê a equipe. Não somar contagem ainda não salva nem duplicar registros ao combinar projetos.

R4. Pessoas inativas ou removidas permanecem nos totais e na seção de horas da equipe quando há apontamentos elegíveis. Participantes atuais sem horas aparecem com zero. Projetos em que o usuário é membro contribuem somente com suas próprias horas.

R5. Atraso exige prazo anterior a hoje e situação Pendente, Em andamento ou Pausada. Canceladas e Arquivadas não compõem atraso ou progresso; Finalizadas não são atrasadas.

R6. Finalizadas no período usa data de finalização inclusiva em Brasília e somente o recorte autorizado de tarefas. Período inicial = hoje e 29 dias corridos anteriores. Nenhum outro indicador recebe esse filtro temporal.

R7. Ambas as datas são obrigatórias e início deve ser menor ou igual ao fim. Datas futuras são permitidas. Aplicar pelo botão, preservar durante o acesso atual e restaurar o padrão no novo login. Erros preservam campos e não aplicam intervalo inválido.

R8. Progresso = Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas) × 100, no recorte do projeto. Vazio = 0%. Arredondar ao inteiro mais próximo e mostrar contagem finalizadas/total.

R9. Listar oito projetos por página em ordem alfabética. Paginação não limita indicadores gerais nem o cálculo de totais. Projetos sem dados elegíveis não desaparecem por esse motivo.

R10. Totais gerais são informativos; atalhos de situação/atraso por projeto aplicam seus filtros e responsável pessoal quando necessário, substituindo o contexto anterior da consulta. Finalizadas no período permanece informativo. Links respeitam o acesso vigente e não criam novos filtros de data ou permissões.

R11. Cards e gráficos identificam valores e alcance pessoal/de equipe; esforço compara os totais estimados e realizados sem transferir autoria após reatribuição. Campos sem valor não acrescentam horas; ausência de dados não é erro, e erro não é anunciado como zero válido.

## Dados percebidos pelo usuário

Projetos ativos, distribuição nas cinco situações, quantidade de atrasadas, Finalizadas no período, datas inicial/final e botão de aplicação, horas estimadas e realizadas, horas por pessoa e progresso por projeto. Cards com identificador, nome, estado, gestor, prazo, finalizadas/total, percentual e horas realizadas no recorte. Paginação, links de projeto e consultas por situação/atraso e Minhas Tarefas. Identificação de alcance, gráficos rotulados, estados de carregamento, vazio, erro, indisponibilidade e sucesso; conteúdo empilhado no mobile.

## Critérios de aceite

CA1 — Como gestor em A e membro em B, ao abrir o painel, incluir tarefas e horas da equipe de A, mas somente tarefas atualmente próprias e horas registradas por si em B. Não expor horas alheias de B por causa da gestão de A. [R1–R4]

CA2 — Como administrador ativo sem participação, ao abrir, incluir todos os projetos ativos e suas equipes. Como usuário comum, excluir projetos sem acesso. Conta inativa não consulta o painel por acesso direto. [R1]

CA3 — Com projetos ativos sem tarefas e projetos arquivados com dados, ao consultar, contar os ativos sem tarefas e excluir os arquivados de todos os indicadores e cards. Projetos ativos sem dados elegíveis apresentam zero/vazio conforme o indicador. [R1, R9]

CA4 — Com tarefas nas cinco situações e tarefas Arquivadas, ao consultar distribuição, incluir Pendente, Em andamento, Pausada, Finalizada e Cancelada e excluir Arquivadas, dentro do recorte autorizado. [R2]

CA5 — Com estimativas e apontamentos em Canceladas e Arquivadas de projeto ativo, ao consultar esforço, incluir os das Canceladas e excluir os das Arquivadas. Ambas permanecem fora do progresso e atraso. [R2–R3, R5]

CA6 — Com tarefa reatribuída de um membro para outra pessoa, ao consultar o painel do primeiro, retirar a tarefa de suas quantidades, estimativas e progresso pessoais, mantendo suas horas registradas enquanto tarefa/projeto forem elegíveis e houver acesso. Não transferir essas horas ao novo responsável. [R2–R3, R11]

CA7 — Com apontamentos próprios e alheios na mesma tarefa, ao consultar como membro, somar somente os próprios. Como gestor do projeto ou administrador, somar os registros da equipe autorizada, sem duplicação. [R3]

CA8 — Com pessoa inativa ou removida e apontamentos elegíveis, ao consultar como gestor/administrador, manter suas horas na seção por pessoa. Participante atual sem horas aparece com zero; membro não vê linhas alheias no seu recorte. [R4]

CA9 — Com cronômetro em contagem, ao consultar realizadas, somar somente apontamentos salvos. Após salvar/corrigir/excluir um apontamento pela capacidade responsável, uma nova consulta reflete os registros atuais. [R3]

CA10 — Com prazo passado nas situações Pendente, Em andamento, Pausada, Finalizada e Cancelada, ao consultar atraso, contar somente as três primeiras. Prazo de hoje, futuro, ausente ou tarefa Arquivada não entra. [R5]

CA11 — Com hoje em 10/09/2026 e sem período preservado, ao abrir, usar 12/08/2026 a 10/09/2026, inclusive, em Brasília. Contar finalizações no intervalo pela data de finalização, não pelo prazo. [R6]

CA12 — Ao alterar e aplicar o período, atualizar somente Finalizadas no período. Distribuição, atrasos, horas, estimativas e progresso permanecem calculados sem esse corte temporal. [R6]

CA13 — Ao enviar data ausente, inválida ou início posterior ao fim, não aplicar e mostrar erro com campos preservados. Com início igual ao fim, consultar esse dia; com datas futuras válidas sem finalizações, apresentar zero. [R7]

CA14 — Com período alterado, ao navegar e recarregar, preservá-lo durante o acesso atual. Após sair e entrar novamente, restaurar hoje e os 29 dias anteriores. [R7]

CA15 — Com uma Finalizada e duas tarefas elegíveis não finalizadas, ao consultar progresso, mostrar 1/3 e 33%. Com duas Finalizadas em três, mostrar 2/3 e 67%. Acrescentar Canceladas ou Arquivadas não altera o cálculo. [R8]

CA16 — Com denominador vazio ou somente Canceladas, ao consultar progresso, mostrar 0%. Para membro, usar apenas suas tarefas atuais; para gestor/administrador, usar a equipe do projeto. [R2, R8]

CA17 — Com mais de oito projetos ativos elegíveis, ao percorrer a lista, mostrar oito por página em ordem alfabética e manter os indicadores gerais sobre todos os projetos, sem redução ao tamanho da página. [R9]

CA18 — Ao abrir um card de projeto, navegar ao projeto autorizado. Com perda de acesso antes da abertura, recusar o destino restrito. [R1, R10]

CA19 — Com filtros antigos na Consulta de Tarefas, ao acionar um atalho de situação por projeto, substituir pelo projeto e situação correspondentes; incluir o próprio responsável quando membro e usar equipe quando gestor/administrador. [R10]

CA20 — Ao acionar atraso de um projeto, abrir a consulta com projeto, Apenas atrasadas e responsável pessoal quando aplicável, sem filtros anteriores que alterem o resultado. Não usar Prazo até como substituto indevido da regra de atraso. [R5, R10]

CA21 — Ao consultar totais gerais e Finalizadas no período, apresentá-los como informativos, sem abrir lista que perca recorte ou data. O link Minhas Tarefas abre sua visão pessoal existente. [R10]

CA22 — Com realizados superiores aos estimados ou horas antigas após reatribuição, ao comparar esforço, mostrar os valores reais e identificar o alcance, sem limitar realizadas à estimativa ou transferir autoria. [R3, R11]

CA23 — Sem dados elegíveis, ao consultar, apresentar zeros/vazios. Em falha, apresentar erro e permitir nova tentativa com período preservado, sem confundir falha com zero ou sucesso. [R11; exceções]

CA24 — Em desktop/mobile, ao consultar indicadores, gráficos, cards e filtros, apresentar valores rotulados e alcance compreensível, com conteúdo empilhado no mobile, teclado, foco e mensagens acessíveis. Não depender apenas de cor. [Dados percebidos; guia]

## Dependências

Consulta de Tarefas (#1014465) e Minhas Tarefas (#1014547), com relações nativas aprovadas e conferidas: 669, #1014465 bloqueia #1014550; 670, #1014547 bloqueia #1014550. Fornecem destinos de navegação e recortes já entregues. Dados, situações, atribuições, datas, projetos e apontamentos vêm das capacidades anteriores por essa cadeia.

O painel não exige novo filtro de data de finalização na Consulta de Tarefas. Seus atalhos aplicam filtros existentes; o indicador de finalizações no período permanece informativo. O quadro do projeto continua uma capacidade separada, sem nova relação bloqueadora neste requisito.

## Designs e evidências

- [Painel](../../scopes/2026-09-09-nexum-scope/sources/design-dashboard.md), [guia](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md) e [apontamentos](../../scopes/2026-09-09-nexum-scope/sources/design-time-entries.md).
- [Entrevista](interview.md): Q111–Q120 e confirmação explícita do entendimento por Mário Tinelli.
- [Catálogo revisado aprovado](../../scopes/2026-09-09-nexum-scope/catalog-time-review.md): recortes por papel, situações e fórmula de progresso.
- Q111 fecha papéis mistos; Q112 limita a projetos ativos; Q113/Q119 definem período e uso; Q114/Q115 definem paginação e arredondamento; Q116–Q118 definem populações de tarefas e horas; Q120 limita atalhos aos recortes suportados. Regras antigas de perfis e situações nas referências são substituídas pelos requisitos aprovados.

## Dentro do escopo

Painel agregado por papel/projeto ativo, distribuição, atrasos, finalizações por período, esforço, horas por pessoa, progresso, paginação de projetos e navegação autorizada. Interface WEB responsiva em português com estados de carregamento, vazio, erro, indisponibilidade e sucesso. Aplicam-se as exigências explícitas do guia: contraste WCAG AA, teclado, foco visível, labels, nomes acessíveis, rótulos sem depender só de cor, alvos de toque, hierarquia semântica e redução de movimento.

## Fora do escopo

Projetos arquivados no painel, tarefas arquivadas nos indicadores, produção ou edição de tarefas/apontamentos, alteração de permissões, aprovação de horas, faturamento ou centros de custo. Não criar filtro de data de finalização na consulta, atalho agregado com alcance diferente, percentual adicional de desempenho, notificações ou integração externa. Sem aplicativo nativo, API pública ou escolhas de implementação neste requisito.

# [WEB] [OPERACIONAL] Consulta de Tarefas

Issue: #1014465.

## Objetivo

Permitir que participantes encontrem tarefas entre os projetos aos quais têm acesso, combinando busca, filtros, ordenação e paginação pela interface WEB em português. A consulta oferece acesso ao detalhe e preserva o contexto da navegação, respeitando a participação vigente ou o acesso administrativo e as regras de situação e atraso da Gestão de Tarefa.

## Resultado esperado

Encontrar tarefas não arquivadas por trechos de título ou descrição e pelos filtros disponíveis, consultar seus dados essenciais e abrir o detalhe. A mesma consulta funciona em tabela no desktop e cards rotulados no mobile. A busca abrange os projetos acessíveis, incluindo projetos arquivados disponíveis somente para consulta.

## Atores e permissões

- Participantes autenticados e ativos, com papel Membro ou Gestor: consultam somente tarefas dos projetos dos quais participam.
- Administradores ativos: consultam tarefas de qualquer projeto, mesmo sem participação. Projetos arquivados continuam somente para consulta e tarefas arquivadas permanecem fora dos resultados.
- Gestores de projeto ativo e administradores: acessam Nova tarefa conforme a Gestão de Tarefa. A consulta não concede novas permissões de criação, edição, atribuição ou execução.
- Conta inativa ou pessoa sem acesso vigente: não pode consultar o conteúdo restrito, inclusive por acesso direto ou tela já aberta.

Projetos arquivados mantêm consulta; tarefas arquivadas não entram nos resultados. A abertura de detalhes aplica as permissões e limitações da Gestão de Tarefa.

## Histórias de usuário

1. Como participante ou administrador, quero buscar trechos do título ou da descrição para localizar uma tarefa mesmo sem lembrar seu nome completo.
2. Como participante ou administrador, quero combinar filtros de projeto, responsável, situação, prioridade, prazo e atraso para reduzir os resultados ao trabalho procurado.
3. Como participante ou administrador, quero localizar tarefas sem responsável e atribuições antigas a pessoas inativas para consultar sua distribuição.
4. Como participante ou administrador, quero ordenar por criação, atualização, prazo ou prioridade para examinar os resultados na sequência adequada.
5. Como participante ou administrador, quero percorrer os resultados paginados e voltar do detalhe ao mesmo contexto para continuar a consulta.
6. Como participante ou administrador, quero abrir Ver tarefas de um projeto com esse contexto aplicado para encontrar suas tarefas sem interferência de filtros anteriores.
7. Como gestor autorizado ou administrador, quero acessar Nova tarefa pela consulta para iniciar o cadastro entregue pela Gestão de Tarefa.

## Fluxo principal

**Entrada geral:** abrir Consulta de Tarefas. Sem filtros preservados do acesso atual, iniciar com busca vazia, todos os projetos acessíveis, todas as situações e prioridades admitidas, Todos os responsáveis, Prazo até vazio e Apenas atrasadas desmarcado. A ordenação padrão é criação mais recente, na primeira página.

**Busca e filtros:** preencher o texto e selecionar filtros de projeto, responsável, situação, prioridade, Prazo até e Apenas atrasadas. Os filtros são combinados: cada tarefa deve satisfazer todas as restrições preenchidas. Acionar Aplicar filtros para atualizar o resultado e voltar à primeira página. A busca encontra o trecho no título ou na descrição, ignorando maiúsculas/minúsculas, acentos e espaços nas extremidades.

**Responsável:** oferecer Todos, Sem responsável e pessoas dos projetos acessíveis, incluindo responsáveis inativos que ainda tenham tarefas. Ao selecionar um projeto, limitar as opções a ele. Se o responsável escolhido continuar válido, mantê-lo; caso contrário, redefinir para Todos, preservando os demais filtros. Sem responsável filtra tarefas sem atribuição.

**Resultados:** apresentar título com acesso ao detalhe, situação, responsável, prazo, prioridade e indicação de atraso. Mostrar oito tarefas por página, total encontrado e Anterior/Próxima conforme a existência de páginas. No mobile, apresentar cards com rótulos equivalentes. Sem responsável e Sem prazo são identificados como tais.

**Ordenação:** usar criação mais recente como padrão; oferecer atualização mais recente, prazo crescente com tarefas sem prazo no fim e prioridade de Urgente para Baixa. Em empate, usar criação mais recente.

**Detalhe e retorno:** abrir o detalhe da tarefa pela ação do título. Ao voltar à consulta, preservar os filtros e a página. Se essa página deixar de existir devido a mudanças nos resultados, abrir a última disponível; sem resultados, apresentar o estado vazio.

**Entrada pelo projeto:** ao abrir Ver tarefas de um projeto, aplicar somente o filtro desse projeto e limpar os demais filtros anteriores. Essa entrada substitui o contexto preservado da consulta. O usuário pode alterar ou limpar os filtros depois, dentro de seus projetos acessíveis.

**Limpeza e continuidade:** Limpar remove busca e filtros, restaura a ordenação padrão e volta à primeira página. Preservar filtros e ordenação ao navegar e atualizar a página durante o acesso atual. Sair da conta e entrar novamente restaura o padrão.

**Nova tarefa:** oferecer o acesso conforme a permissão de gestor do projeto ativo ou administrador. Cadastro, validações e resultado da criação pertencem à Gestão de Tarefa; esta Feature oferece a navegação para esse fluxo.

## Fluxos alternativos e exceções

- Busca ou combinação de filtros sem correspondência: apresentar nenhum resultado e permitir Limpar filtros.
- Nenhuma tarefa acessível: apresentar estado vazio; acesso a Nova tarefa segue as permissões existentes.
- Pessoa perde participação sem possuir acesso administrativo, perde o acesso administrativo sem participação ou conta fica inativa: a consulta e a abertura direta de detalhes não mantêm acesso ao conteúdo que deixou de ser permitido.
- Projeto arquivado: manter suas tarefas não arquivadas disponíveis para consulta; abrir detalhe respeita somente leitura.
- Tarefa arquivada após aparecer na consulta: ela deixa de compor novos resultados; seu detalhe segue a regra de consulta da Gestão de Tarefa.
- Responsável inválido após trocar o projeto: redefinir somente esse filtro para Todos. Entrar por Ver tarefas do projeto continua seguindo a limpeza contextual própria desse fluxo.
- Prazo até preenchido: tarefas sem prazo não correspondem ao filtro. Prazo da tarefa igual à data informada corresponde.
- Carregamento, falha ou indisponibilidade: apresentar estado e mensagem apropriados; falha não indica sucesso e permite nova tentativa, preservando os filtros para correção ou reaplicação.
- A página anteriormente aberta deixa de existir: usar a última disponível, ou estado vazio se nenhuma tarefa corresponder.

## Regras de negócio

R1. Consultar somente tarefas não arquivadas de projetos com participação vigente; administradores ativos consultam qualquer projeto, independentemente de participação. Projetos arquivados continuam acessíveis para consulta; administração não concede participação automática. As restrições também valem para acessos diretos.

R2. A busca considera qualquer trecho do título ou da descrição, ignorando maiúsculas/minúsculas, acentos e espaços nas extremidades. Basta corresponder em um desses campos. Busca vazia não restringe a consulta.

R3. Projeto, responsável, situação e prioridade têm seleção única, além das opções gerais. Combinar os filtros preenchidos por E; a correspondência entre título e descrição é por OU. Os filtros operam apenas sobre o conjunto permitido por R1.

R4. Responsável oferece Todos, Sem responsável e pessoas dos projetos acessíveis, incluindo responsáveis inativos com tarefas. Selecionar projeto limita as pessoas a esse projeto. Trocar projeto mantém o responsável válido ou redefine o inválido para Todos, preservando os demais filtros.

R5. Situações consultáveis: Pendente, Em andamento, Pausada, Finalizada e Cancelada. Prioridades: Baixa, Média, Alta e Urgente. Sem filtro de situação, todas essas situações participam da consulta. Arquivada não é oferecida como situação de resultado nesta entrega.

R6. Prazo até é inclusivo e, quando informado, exclui tarefas sem prazo. Apenas atrasadas exige prazo anterior à data atual e situação Pendente, Em andamento ou Pausada. Finalizadas e canceladas não são atrasadas; prazo de hoje, futuro ou ausente não caracteriza atraso.

R7. Ordenação padrão por criação decrescente. Outras opções: atualização decrescente; prazo crescente, sem prazo por último; prioridade Urgente, Alta, Média e Baixa. Em empate, criação mais recente primeiro.

R8. Paginação fixa de oito tarefas, com total encontrado e controles Anterior/Próxima. Aplicar ou limpar filtros volta à primeira página. Retorno do detalhe preserva filtros e página; página inexistente passa à última disponível, ou estado vazio quando não houver resultados.

R9. Entrada por Ver tarefas do projeto aplica somente esse projeto e limpa o contexto anterior. Limpar remove busca/filtros, restaura ordenação padrão e primeira página. As opções de projeto respeitam participação vigente ou acesso administrativo.

R10. Preservar filtros e ordenação ao navegar e atualizar durante o acesso atual. Sair e entrar novamente restaura os valores iniciais. Entrada contextual pelo projeto e Limpar são exceções explícitas à preservação.

R11. Resultados apresentam título, situação, responsável, prazo, prioridade, atraso e acesso ao detalhe. Criação e manutenção da tarefa, ações de situação, colaboração e execução permanecem nas capacidades responsáveis, com as permissões aprovadas.

## Dados percebidos pelo usuário

Campo de busca, seleções de projeto, situação, prioridade e responsável, Prazo até, Apenas atrasadas, ordenação, Aplicar filtros e Limpar. Resultados com título, situação, responsável ou Sem responsável, prazo ou Sem prazo, prioridade, indicação de atraso, total encontrado, paginação e acesso ao detalhe. Nova tarefa aparece conforme permissão. Tabela no desktop e cards equivalentes no mobile; mensagens de carregamento, vazio, erro, indisponibilidade e sucesso.

## Critérios de aceite

CA1 — Com participante ativo em diferentes projetos, ao abrir a consulta, apresentar somente suas tarefas não arquivadas, incluindo as de projetos arquivados. Projetos sem participação permanecem inacessíveis para usuários comuns; administradores consultam tarefas de todos os projetos, respeitando as exclusões de situação. [R1]

CA2 — Sem filtros preservados, ao abrir, usar valores gerais, busca/prazo vazios, Apenas atrasadas desmarcado, criação mais recente e primeira página. Finalizadas e canceladas aparecem quando pertencem ao conjunto permitido. [R5, R7–R10; entrada]

CA3 — Com “Revisão do contrato” somente no título de uma tarefa e somente na descrição de outra, ao buscar “ revisao ”, encontrar ambas, respeitando os demais filtros e o acesso. Texto sem correspondência não as encontra; busca vazia não restringe. [R2–R3]

CA4 — Com filtros simultâneos, ao Aplicar, retornar somente tarefas que satisfaçam todas as restrições preenchidas, com busca correspondente no título ou na descrição, e abrir a primeira página. [R3, R8]

CA5 — Ao abrir filtro de responsável, oferecer Todos, Sem responsável e as pessoas permitidas, incluindo inativos com tarefas. Ao escolher Sem responsável, retornar somente tarefas sem atribuição. [R4]

CA6 — Com responsável escolhido, ao trocar projeto, restringir as pessoas ao novo projeto; manter a seleção se válida ou redefinir para Todos se inválida, preservando os outros filtros. [R4]

CA7 — Ao informar Prazo até, incluir tarefas com prazo anterior ou igual à data e excluir tarefas com prazo posterior ou ausente. Ao combinar Apenas atrasadas, cumprir também a regra de atraso. [R3, R6]

CA8 — Ao usar Apenas atrasadas, retornar somente Pendentes, Em andamento ou Pausadas com prazo anterior à data atual. Excluir Finalizadas, Canceladas e tarefas com prazo de hoje, futuro ou ausente. [R6]

CA9 — Ao selecionar cada ordenação, apresentar criação/atualização mais recente primeiro, prazo crescente com sem prazo no fim ou prioridades Urgente→Alta→Média→Baixa. Em empate, apresentar criação mais recente primeiro. [R7]

CA10 — Com mais de oito correspondências, ao consultar e avançar, apresentar até oito tarefas por página e total encontrado; Anterior/Próxima refletem páginas disponíveis. Aplicar ou limpar filtros retorna à primeira. [R8]

CA11 — Após abrir o detalhe a partir de uma página filtrada, ao voltar, preservar filtros e página. Se ela não existir mais, abrir a última disponível; sem correspondências, mostrar vazio. [R8]

CA12 — Com filtros anteriores de outro contexto, ao entrar por Ver tarefas de um projeto acessível, aplicar somente esse projeto e limpar os demais filtros. Depois, permitir alterar ou limpar a consulta. [R9]

CA13 — Com busca, filtros e ordenação alterados, ao navegar ou atualizar a página, mantê-los. Após sair e entrar novamente, restaurar o padrão. Ao Limpar, remover busca/filtros, restaurar ordenação e primeira página. [R9–R10]

CA14 — Sem correspondências, ao consultar, mostrar estado vazio e permitir limpeza dos filtros. Em falha, mostrar erro e permitir nova tentativa com os filtros preservados. [Fluxos alternativos]

CA15 — Com pessoa sem acesso vigente ou conta inativa, ao consultar ou abrir diretamente tarefa restrita, recusar. Com projeto arquivado acessível, ao abrir detalhe, manter somente consulta conforme Gestão de Tarefa. [R1, R11]

CA16 — Como gestor autorizado de projeto ativo ou administrador, ao acionar Nova tarefa, abrir o cadastro da Gestão de Tarefa. Quem não tem essa permissão não recebe autorização de criação pela consulta. [R11]

CA17 — Em desktop/mobile, ao usar busca, filtros, tabela/cards, paginação e links, apresentar os mesmos dados essenciais e ações utilizáveis por teclado, com labels, foco visível e mensagens acessíveis. Diferenciar carregamento, vazio, erro e sucesso. [R11; guia de design]

## Dependências

Gestão de Tarefa (#1014454), com relação nativa 665 já criada e conferida: #1014454 bloqueia #1014465. Fornece dados, situações, prioridades, atribuição, datas, atraso, detalhe e criação autorizada. A participação, o acesso administrativo e o estado dos projetos vêm da Gestão de Projeto por essa integração. Minhas Tarefas e Painel Gerencial mantêm suas próprias entregas e consomem a consulta quando previsto no catálogo, sem alterar seus limites de acesso.

## Designs e evidências

- Revisão administrativa: Q84/Q95 e entendimento confirmado na [entrevista de Gestão de Tempo](../1014493-gestao-de-tempo/history/interview.md), com [catálogo revisado aprovado](../../scopes/2026-09-09-nexum-scope/.flow/reviews/catalog-time-review.md). Essa decisão substitui a limitação anterior do administrador aos projetos participantes.
- [Tela Tarefas](../../scopes/2026-09-09-nexum-scope/sources/design-tasks.md) e [Guia de design](../../scopes/2026-09-09-nexum-scope/sources/design-guide.md).
- [Entrevista](history/interview.md): decisões Q63–Q69 e confirmação explícita de Mário Tinelli.
- [Catálogo completo revisado aprovado](../../scopes/2026-09-09-nexum-scope/.flow/reviews/catalog-search-review.md).
- Q63 amplia a busca do protótipo e do catálogo antigo para título ou descrição, ignorando acentos. Q64/Q69 definem opções e redefinição de responsável. Q65/Q66 confirmam ordenação, oito registros por página e continuidade. Q67/Q68 resolvem precedência do projeto e duração da preservação dos filtros. Situações e permissões antigas das referências são substituídas pelas já aprovadas na Gestão de Tarefa.

## Dentro do escopo

Consulta transversal, busca por título/descrição, filtros combinados, ordenação, paginação, preservação de contexto, navegação contextual do projeto e acesso ao detalhe e à criação permitida. Interface WEB responsiva em português com tabela/cards, carregamento, vazio, erro, indisponibilidade e sucesso. Aplicam-se os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento.

## Fora do escopo

Criação e edição de dados de tarefa, atribuição, ações de situação, comentários, anexos, histórico, cronômetro e apontamentos nesta tela; pertencem às respectivas Features, acessíveis pela navegação quando entregue. Agrupamentos e execução diária de Minhas Tarefas, Quadro do Projeto e Painel Gerencial permanecem nas capacidades responsáveis. Tarefas arquivadas não integram estes resultados. Sem aplicativo nativo, API pública ou escolhas de implementação neste requisito.

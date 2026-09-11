# Revisão explícita do catálogo Nexum

Revisão solicitada em 09/09/2026 por Mário Tinelli, concluída com sua aprovação explícita e aplicada ao [catálogo canônico](scope.md). A aprovação está registrada como `catalog-review-approval-2026-09-09` em [scope-state.json](scope-state.json).

O ponto de partida era um catálogo legado com 13 Features pendentes, sem aprovação, issue criada ou entrevista iniciada. Naquele estado, `catalog-approved` indicava a próxima fase incompleta. Agora essa fase está concluída e o catálogo contém 11 Features ativas aprovadas.

## Achados e impacto

| Achado | Evidência | Impacto na revisão |
| --- | --- | --- |
| Cronômetro e apontamentos não têm responsável no catálogo. | `sources/design-dashboard.md`, seção Cálculos e perfis; `sources/design-edit-project.md`, seção Permissões e falhas declaradas; `sources/design-profile.md`, navegação. | Resolver inclusão ou exclusão antes da aprovação: afeta painel, horas de projetos/cards e impedimento de arquivamento. Não cabe relegar a origem das horas à entrevista do painel. |
| Há referências funcionais fora das 12 fontes inventariadas. | `sources/design-profile.md`, Minhas tarefas e Apontamentos; fontes de criação/listagem encaminham a detalhes; `sources/design-new-task.md` menciona um guia. Os HTMLs originais de painel e nova tarefa referenciam `minhas-tarefas`, `apontamentos`, `detalhes-projeto` e `detalhes-tarefa`. | Pedir inclusão dos materiais referenciados ou exclusão explícita. Arquivos vizinhos não são incorporados automaticamente. |
| O teste de remover uma operação foi usado como justificativa principal para separar capacidades. | `scope.md`, Decisões dos candidatos; `browse-projects`, `create-project`, `update-project`, `archive-reactivate-project`, `create-task`, `update-task`. | Propor Gestão de Projeto reunindo consulta, criação, manutenção e ciclo de vida. Avaliar Gestão de Tarefa reunindo criação, detalhe e edição. Preservar IDs antigos e registrar eventuais fusões somente após decisão. |
| Não há convenção confirmada de superfície e público. | Títulos e atores do catálogo legado. | Confirmar WEB e prefixos PUBLICO, ADMIN e OPERACIONAL; o significado agregado de OPERACIONAL precisa ser explícito. Diferenças gestor/membro permanecem em cada entrega. |
| Alocar arquivos não comprova cobertura de comportamentos. | Todas as fontes foram marcadas compartilhadas; não há inventário por comportamento. | Enriquecer com ações, estados, navegação, regras e ambiguidades, um responsável por comportamento e consumidores separados. Manter as fontes físicas intactas nesta etapa. |
| O grafo ainda não justifica bloqueios de entrega integrada. | `browse-projects` depende só de login apesar de exibir progresso/horas e abrir detalhes; `view-management-dashboard` depende só de criar tarefa apesar de consumir apontamentos. | Reavaliar arestas após resolver limites e origem das horas. Dados ilustrativos não provam entrega independente. Não publicar as 11 relações planejadas sem essa revisão. |
| Parte da base funcional já existe no repositório. | `routes/auth.php`, `routes/web.php`, `docs/agents/domain_rules.md`; testes de autenticação, recuperação, perfil e usuários listados no repositório. | Marcar existência parcial e esclarecer a adaptação ao Nexum. Não classificar como concluído ou Bug apenas pela presença de código/testes. |
| Algumas incertezas mudam público e cobertura. | `sources/design-new-task.md`: gestor versus membro para criar; `sources/design-dashboard.md`: visão reduzida do membro. | Resolver público e alcance no catálogo; deixar validações detalhadas e conflitos de edição para as futuras entrevistas. |

## Direção discutida no início da revisão

| Itens atuais | Direção de revisão |
| --- | --- |
| `authenticate`, `recover-access`, `maintain-own-profile` | Manter objetivos distintos; adotar nomes nominais e explicitar adaptação da base existente. |
| `administer-users` | Gestão de Usuário, incluindo cadastro, consulta, edição e situação/acesso. |
| `browse-projects`, `create-project`, `update-project`, `archive-reactivate-project` | Propor uma Gestão de Projeto coesa. Indicadores consumidos precisam de dependências ou limites explícitos. |
| `create-task`, `update-task` | Propor Gestão de Tarefa e avaliar detalhe/histórico/ciclo de vida após reconciliar as referências. |
| `search-tasks` | Preservar a consulta transversal; distinguir de Minhas Tarefas quando o material referenciado for incluído. |
| `manage-project-board` | Avaliar quadro como entrega própria, com mudança de situação pertencendo a um único responsável e consumida pelas outras telas. |
| `view-management-dashboard` | Painel Gerencial, com audiência e origem das horas resolvidas antes da aprovação. |
| Referências a tempo e consultas pessoais | Candidatos pendentes; não criar novas Features antes da confirmação de cobertura. |

Essa direção inicial foi consolidada no catálogo final de 11 Features, na ordem aprovada abaixo. As fusões conservaram os IDs anteriores como entradas endereçáveis e preservaram fontes, histórico e caminhos. Não existem issues a encerrar, reaproveitar ou alterar.

## Decisões confirmadas na revisão

Mário Tinelli respondeu “concordo com tudo” às propostas de incluir as cinco referências, reagrupar operações por capacidades coesas e usar os prefixos `[WEB] [PUBLICO]`, `[WEB] [ADMIN]` e `[WEB] [OPERACIONAL]`.

Depois confirmou: “Sim, gestores e membros podem criar, mas com permissoes :: Sim, usar esse recorte”. A proposta permite criação de tarefas conforme permissões; membros veem suas tarefas e horas no painel, enquanto gestores veem a equipe dos projetos que gerenciam. A granularidade das permissões será detalhada na entrevista da Gestão de Tarefa, sem pressupor que todo membro pode criar sem autorização.

O usuário também determinou que, após uma pergunta, a execução deve parar até a resposta. Essas confirmações estão registradas na pausa do estado canônico, posteriormente retomada. A aprovação da projeção integral veio em resposta separada: “aprovado”.

## Reconciliação das cinco fontes incluídas

| Fonte nova | Confirma | Complementa ou corrige a interpretação anterior |
| --- | --- | --- |
| `design-guide` | Perfis por projeto, acesso restrito, projetos/tarefas e indicadores. | O MVP inclui explicitamente Minhas Tarefas, cronômetro, apontamentos, comentários e histórico. Origem das horas e execução não podem ser adiadas como incertezas locais do painel. Contém também os limites do MVP; as sugestões de modelo/arquitetura são contexto, não decisões aprovadas nesta revisão. |
| `design-my-tasks` | Busca, filtros e navegação para tarefa. | Acrescenta o recorte de responsabilidade pessoal, seis grupos de trabalho e ações de execução. Não se confunde com a consulta transversal. |
| `design-time-entries` | Soma de horas e navegação por tarefa. | Acrescenta cadastro, edição/exclusão própria, filtros, total do período, origem e apresentação em tarefa/projeto. |
| `design-project-detail` | Consulta do projeto, participantes e restrição de arquivados. | Expõe abas e integrações: Gestão de Projeto entrega dados/participantes; Gestão de Tarefa integra tarefas/progresso; Gestão de Tempo integra horas. |
| `design-task-detail` | Edição, situações e autorizações do detalhe. | Expõe comentários, histórico, arquivamento e cronômetro. Os scripts estáticos também demonstram unicidade do identificador de projeto, validação de datas e impedimento de remover responsável sem reatribuir tarefas, omitidos nas normalizações antigas. Essas fontes antigas permanecem como histórico, e a evidência nova corrige sua leitura. |

As ambiguidades de público de criação e do painel foram resolvidas pelo usuário. Detalhes como arredondamento de tempo, granularidade de permissões, conflito de edição e políticas de senha permanecem para as entrevistas dos itens; não há autorização para inventá-los.

## Catálogo aprovado em ordem de entrega

Este quadro orienta a leitura. A [projeção integral aprovada](catalog-preview.review.md) contém o conteúdo completo: 11 Features ativas, 59 registros de comportamento, 17 fontes, seis entradas legadas retiradas, convenção, entregas, alocação e justificativas de grafo/ordem.

| Ordem | Título | Bloqueios diretos |
| --- | --- | --- |
| 1 | [WEB] [PUBLICO] Autenticação | Nenhum; aproveita a base de contas e a entrada autenticada existente. |
| 2 | [WEB] [PUBLICO] Recuperação de Acesso | Nenhum; aproveita a base e o login existentes. |
| 3 | [WEB] [OPERACIONAL] Meu Perfil | Autenticação. |
| 4 | [WEB] [ADMIN] Gestão de Usuário | Autenticação. |
| 5 | [WEB] [OPERACIONAL] Gestão de Projeto | Gestão de Usuário. |
| 6 | [WEB] [OPERACIONAL] Gestão de Tarefa | Gestão de Projeto. |
| 7 | [WEB] [OPERACIONAL] Consulta de Tarefas | Gestão de Tarefa. |
| 8 | [WEB] [OPERACIONAL] Gestão de Tempo | Gestão de Tarefa. |
| 9 | [WEB] [OPERACIONAL] Minhas Tarefas | Gestão de Tempo. |
| 10 | [WEB] [OPERACIONAL] Quadro do Projeto | Gestão de Tempo. |
| 11 | [WEB] [OPERACIONAL] Painel Gerencial | Minhas Tarefas e Consulta de Tarefas. |

Os dez bloqueios propostos consideram a entrega integrada. Cronômetro e horas precisam existir para aceitar as ações diárias e os cards com horas; o painel depende dos recortes para os quais navega. Dependências transitivas não são repetidas. Esta ordem é uma proposta baseada no uso e nas dependências, não uma prioridade comercial atribuída ao usuário.

### Responsabilidade pelas telas compartilhadas

- Gestão de Projeto entrega os vínculos consultados na tela de usuários. Gestão de Usuário não exige projetos previamente implementados para cadastrar/ativar pessoas.
- Gestão de Tarefa entrega a aba de tarefas, o progresso por quantidade e a proteção contra remoção de responsáveis em projetos. Inclui comentários e histórico no detalhe da tarefa.
- Gestão de Tempo entrega cronômetro, apontamentos, totais e impedimentos de concluir/arquivar com execução aberta, inclusive nas telas já existentes.
- Minhas Tarefas, Quadro e Painel consomem essas capacidades. Cada comportamento tem um responsável; o consumo por outra tela não cria uma segunda autoria.

### Preservação de identidades

`browse-projects`, `create-project`, `update-project` e `archive-reactivate-project` permanecem endereçáveis como entradas retiradas, mapeadas para `manage-project`. `create-task` e `update-task` permanecem retiradas e mapeadas para `manage-task`. Os outros sete IDs antigos continuam ativos. `manage-time` e `my-tasks` são os dois acréscimos funcionais que, junto das duas fusões, resultam em 11 Features ativas.

Não há issues, caminhos de requisitos definitivos ou operações remotas a alterar. As 11 relações antigas continuam preservadas no estado legado. O candidato contém dez relações propostas para o novo grafo, sem publicá-las.

## Validação, bloqueio anterior e correção

- Estado canônico v2: válido, pausado por alteração do catálogo; catálogo, fontes e relações anteriores preservados.
- Candidato v3: válido isoladamente no `validate_scope_state.py`.
- Integridade: os hashes dos originais e normalizações das 17 fontes conferem.
- Projeção integral: gerada por `render_catalog.py` e conferida por `--check`.
- SHA-256 da projeção anterior: `5769807ec312192f9c436a17a84413644e45b62a3b9c0b1f7874e86d07584c53`.
- A primeira tentativa de checagem com `--previous scope-state.json --review-legacy` foi rejeitada com `invalid: legacy review rewrote dependency_graph`.

O validador antigo exigia preservar literalmente o grafo, impedindo o reagrupamento. Mário Tinelli autorizou explicitamente sua correção. O procedimento agora diferencia enriquecimento simples de revisão com uma cópia exata do estado legado em `legacy_review.previous_state`. IDs, fontes, caminhos, progresso e aprovações anteriores continuam protegidos. Relações planejadas não publicadas e não aprovadas podem ficar `retired`, preservando chaves e endpoints; relações publicadas/aprovadas não podem ser retiradas por essa via.

Resultado após a correção:

- 25 testes Python passaram, incluindo fusão, aprovação obrigatória, estado anterior adulterado, perda de IDs/fontes/caminhos, preservação de progresso e proteção das relações publicadas.
- O candidato real passou com `--previous scope-state.json --review-legacy --draft`. A saída informa `valid draft; approval required before replacement`.
- As 11 relações legadas estão preservadas: duas continuam no grafo ativo e nove estão retiradas; oito relações novas completam os dez bloqueios ativos.
- O gerador inclui a identificação do estado anterior e as relações retiradas na projeção; `--check` confirmou o arquivo gerado.
- SHA-256 atual da projeção integral: `4c82e64741b3207bc726a943dd526b96e15e26283d5e37d93cce64ab94120e34`.
- A checagem adicional de empacotamento `quick_validate.py` não pôde executar por falta de PyYAML no Python local. Nenhuma dependência foi instalada; `SKILL.md` permaneceu intacto.

O impedimento de migração foi resolvido. Após a resposta “aprovado”, a alteração e a aprovação foram registradas; a checagem `--previous --review-legacy` passou sem `--draft` e o catálogo foi aplicado. A pausa foi retomada e `catalog-approved` foi adicionado às fases concluídas. O estado agora aguarda o processamento dos itens. Nenhuma publicação no Redmine foi realizada.

## Preservação e validação

- Lock anterior recuperado com confirmação explícita do usuário; novo lock registrado no estado.
- Estado legado v2 validado antes da revisão e preservado integralmente no estado canônico v3; a versão humana anterior está em `scope.legacy.md`.
- Catálogo v3 aprovado e aplicado após checagem completa de preservação. O rascunho separado é um registro preparatório; `scope-state.json` é a autoridade atual.
- Nenhuma mutação realizada no Redmine.

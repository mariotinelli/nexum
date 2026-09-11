# Escopo funcional do Nexum

> Revisão explícita em andamento desde 09/09/2026. O catálogo abaixo é o legado preservado, ainda sem aprovação. Consulte [a revisão](catalog-review.md) e [a proposta integral](catalog-preview.review.md). O estado está pausado por alteração do catálogo; nenhuma issue foi criada. As direções confirmadas pelo usuário estão registradas na pausa de `scope-state.json`.

## Objetivo do escopo

Definir, ordenar e aprovar o catálogo funcional do MVP Nexum a partir dos 12 designs fornecidos, preservando cada jornada vertical como uma Feature independente e rastreável.

## Catálogo proposto

### 1 — `authenticate` — Feature: Autenticar-se no Nexum

- Objetivo humano: permitir que uma pessoa com conta ativa acesse com segurança o ambiente correspondente ao seu perfil.
- Atores: usuário ativo.
- Resultado observável: credenciais válidas levam ao painel; credenciais inválidas ou conta inativa produzem retorno explícito sem conceder acesso.
- Evidências: `design-login`, `design-profile`, `design-recover-password`.
- Dependências diretas: nenhuma.
- Motivo do limite vertical: a autenticação termina no acesso ao ambiente e continua demonstrável mesmo sem recuperação de senha, perfil ou módulos de negócio.
- Estado: pendente.

### 2 — `recover-access` — Feature: Recuperar acesso à conta

- Objetivo humano: permitir que uma pessoa redefina a senha quando não consegue mais acessar sua conta.
- Atores: pessoa com conta cadastrada.
- Resultado observável: a solicitação não revela a existência do e-mail; um vínculo válido permite definir nova senha e retornar ao login, enquanto vínculo inválido ou expirado é informado.
- Evidências: `design-login`, `design-recover-password`.
- Dependências diretas: nenhuma.
- Motivo do limite vertical: recuperar acesso é uma jornada pública e aceitável por si só; removê-la não elimina a autenticação normal.
- Estado: pendente.

### 3 — `maintain-own-profile` — Feature: Manter o próprio perfil

- Objetivo humano: permitir que o usuário autenticado mantenha seus dados pessoais e, quando desejar, altere sua senha.
- Atores: usuário autenticado.
- Resultado observável: nome e e-mail podem ser atualizados; a senha somente muda quando o conjunto de campos de alteração é preenchido e validado.
- Evidências: `design-login`, `design-profile`.
- Dependências diretas: `authenticate`.
- Motivo do limite vertical: a manutenção do próprio cadastro é uma intenção pessoal única e não se confunde com recuperar acesso ou administrar outras pessoas.
- Estado: pendente.

### 4 — `administer-users` — Feature: Administrar usuários

- Objetivo humano: permitir que o administrador consulte e mantenha os cadastros e acessos das pessoas que podem usar o Nexum.
- Atores: administrador.
- Resultado observável: o administrador lista, pagina, cadastra e edita nome, e-mail, estado e acesso administrativo, além de consultar participações em projetos.
- Evidências: `design-login`, `design-users`.
- Dependências diretas: `authenticate`.
- Motivo do limite vertical: cadastro, edição, estado e consulta de participações formam uma jornada coesa de manutenção administrativa do mesmo recurso; não administram projetos em si.
- Estado: pendente.

### 5 — `browse-projects` — Feature: Consultar projetos participantes

- Objetivo humano: permitir que um participante encontre e abra os projetos dos quais faz parte.
- Atores: participante autenticado.
- Resultado observável: a pessoa visualiza somente projetos em que participa, filtra por estado, percorre páginas e abre um projeto com seus indicadores operacionais.
- Evidências: `design-dashboard`, `design-projects`.
- Dependências diretas: `authenticate`.
- Motivo do limite vertical: encontrar e abrir projetos é uma jornada de consulta independente de criar ou modificar qualquer projeto.
- Estado: pendente.

### 6 — `create-project` — Feature: Criar projeto

- Objetivo humano: permitir que um gestor inicie um projeto com identificação, planejamento e participantes definidos.
- Atores: gestor.
- Resultado observável: com os campos obrigatórios válidos, o projeto é criado, o gestor integra obrigatoriamente os participantes e o usuário segue para o projeto criado.
- Evidências: `design-new-project`, `design-projects`, `design-users`.
- Dependências diretas: `authenticate`.
- Motivo do limite vertical: criar o registro e sua composição inicial produz valor próprio e pode ser aceito sem edição posterior, arquivamento ou tarefas.
- Estado: pendente.

### 7 — `update-project` — Feature: Atualizar projeto e participantes

- Objetivo humano: permitir que o gestor participante mantenha os dados, o planejamento e a composição de um projeto ativo.
- Atores: gestor participante.
- Resultado observável: o gestor salva alterações de dados, gestor, participantes e papéis sem permitir que o gestor deixe de participar.
- Evidências: `design-edit-project`, `design-new-project`, `design-projects`.
- Dependências diretas: `create-project`.
- Motivo do limite vertical: a manutenção recorrente do projeto é aceitável sem alterar seu estado de arquivamento; arquivar possui intenção, confirmação e impedimentos próprios.
- Estado: pendente.

### 8 — `archive-reactivate-project` — Feature: Arquivar e reativar projeto

- Objetivo humano: permitir que o gestor retire um projeto do uso operacional sem perder sua consulta e possa reativá-lo depois.
- Atores: gestor participante.
- Resultado observável: o arquivamento exige confirmação, bloqueia mutações e é recusado quando há cronômetro ativo; a reativação devolve o projeto ao uso operacional.
- Evidências: `design-board`, `design-edit-project`, `design-projects`.
- Dependências diretas: `create-project`.
- Motivo do limite vertical: encerrar temporariamente e retomar o uso operacional é uma jornada de ciclo de vida independente da edição dos dados do projeto.
- Estado: pendente.

### 9 — `create-task` — Feature: Criar tarefa

- Objetivo humano: permitir que um participante autorizado registre e planeje uma entrega dentro de um projeto ativo.
- Atores: participante autorizado.
- Resultado observável: a tarefa nasce Pendente, com prioridade Média por padrão, autor automático e responsável limitado aos participantes do projeto, e depois é aberta para consulta.
- Evidências: `design-board`, `design-new-task`, `design-tasks`.
- Dependências diretas: `create-project`.
- Motivo do limite vertical: registrar uma nova entrega produz resultado independente de pesquisar, editar ou movimentar tarefas existentes.
- Estado: pendente.

### 10 — `search-tasks` — Feature: Pesquisar tarefas acessíveis

- Objetivo humano: permitir que um participante encontre tarefas relevantes nos projetos aos quais tem acesso.
- Atores: participante autenticado.
- Resultado observável: a pessoa busca, combina filtros, ordena e pagina somente tarefas acessíveis e não arquivadas, preservando os filtros durante a navegação da página.
- Evidências: `design-dashboard`, `design-tasks`.
- Dependências diretas: `create-task`.
- Motivo do limite vertical: localizar tarefas é uma jornada de consulta demonstrável sem modificar seu conteúdo ou situação.
- Estado: pendente.

### 11 — `update-task` — Feature: Atualizar tarefa

- Objetivo humano: permitir que gestor ou responsável autorizado mantenha o conteúdo, planejamento, atribuição e situação de uma tarefa.
- Atores: gestor participante e responsável pela tarefa.
- Resultado observável: alterações válidas são salvas, o responsável permanece entre participantes, transições de situação respeitam destinos permitidos e conclusão ou reabertura ajusta a data de conclusão.
- Evidências: `design-board`, `design-edit-task`, `design-new-task`.
- Dependências diretas: `create-task`.
- Motivo do limite vertical: manter uma tarefa individual é uma jornada independente de encontrá-la na listagem ou operar várias tarefas no quadro.
- Estado: pendente.

### 12 — `manage-project-board` — Feature: Operar quadro do projeto

- Objetivo humano: permitir que participantes acompanhem as tarefas de um projeto por situação e que pessoas autorizadas atualizem o fluxo diretamente nos cards.
- Atores: participante autenticado, gestor participante e responsável pela tarefa.
- Resultado observável: as tarefas aparecem em Pendente, Em andamento, Bloqueada ou Concluída; a alteração usa controle textual com somente destinos permitidos e projetos arquivados ficam apenas para consulta.
- Evidências: `design-board`, `design-edit-task`.
- Dependências diretas: `create-task`.
- Motivo do limite vertical: a visualização e operação contextual por colunas constituem uma jornada própria, sem substituir a edição detalhada da tarefa.
- Estado: pendente.

### 13 — `view-management-dashboard` — Feature: Acompanhar painel gerencial

- Objetivo humano: permitir que gestores e membros acompanhem, conforme sua visibilidade, progresso, atrasos e esforço dos projetos.
- Atores: gestor e membro.
- Resultado observável: o painel apresenta indicadores, distribuição por situação, esforço da equipe e progresso dos projetos, com filtro de período para conclusões e navegação aos recortes relacionados.
- Evidências: `design-dashboard`, `design-projects`, `design-tasks`.
- Dependências diretas: `create-task`.
- Motivo do limite vertical: acompanhar indicadores agregados é um objetivo analítico independente de consultar registros individuais de projetos ou tarefas.
- Estado: pendente.

## Decisões dos candidatos

- Os 13 candidatos foram classificados como `Feature`; nenhum design demonstra desvio de comportamento existente que sustente um `Bug`.
- Login, recuperação de acesso e manutenção do perfil foram separados porque cada jornada preserva valor se uma das outras for removida.
- Consulta, criação, atualização e arquivamento de projetos foram separados pelo mesmo teste de remoção.
- Criação, pesquisa, atualização e operação das tarefas no quadro também permanecem jornadas independentes.
- O CRUD administrativo de usuários foi mantido junto porque cadastro, edição, estado e consulta de participação são variantes coesas da manutenção do mesmo recurso.

## Alocação das fontes

Todas as fontes são compartilhadas pelo escopo porque cada design sustenta pelo menos duas jornadas ou uma jornada e sua transição funcional adjacente:

| Fonte | Itens apoiados |
| --- | --- |
| `design-board` | `archive-reactivate-project`, `create-task`, `update-task`, `manage-project-board` |
| `design-dashboard` | `browse-projects`, `search-tasks`, `view-management-dashboard` |
| `design-edit-project` | `update-project`, `archive-reactivate-project` |
| `design-edit-task` | `update-task`, `manage-project-board` |
| `design-login` | `authenticate`, `recover-access`, `maintain-own-profile`, `administer-users` |
| `design-new-project` | `create-project`, `update-project` |
| `design-new-task` | `create-task`, `update-task` |
| `design-profile` | `authenticate`, `maintain-own-profile` |
| `design-projects` | `browse-projects`, `create-project`, `update-project`, `archive-reactivate-project`, `view-management-dashboard` |
| `design-recover-password` | `authenticate`, `recover-access` |
| `design-tasks` | `create-task`, `search-tasks`, `view-management-dashboard` |
| `design-users` | `administer-users`, `create-project` |

## Grafo canônico de dependências

```text
authenticate
├── maintain-own-profile
├── administer-users
├── browse-projects
└── create-project
    ├── update-project
    ├── archive-reactivate-project
    └── create-task
        ├── search-tasks
        ├── update-task
        ├── manage-project-board
        └── view-management-dashboard

recover-access
```

As 11 arestas serão projetadas como relações nativas `blocks`, sempre da Feature pré-requisito para a dependente.

## Grupos prontos em paralelo

1. `authenticate`, `recover-access`.
2. Após `authenticate`: `maintain-own-profile`, `administer-users`, `browse-projects`, `create-project`.
3. Após `create-project`: `update-project`, `archive-reactivate-project`, `create-task`.
4. Após `create-task`: `search-tasks`, `update-task`, `manage-project-board`, `view-management-dashboard`.

## Ordem total sugerida

1. `authenticate`
2. `recover-access`
3. `maintain-own-profile`
4. `administer-users`
5. `browse-projects`
6. `create-project`
7. `update-project`
8. `archive-reactivate-project`
9. `create-task`
10. `search-tasks`
11. `update-task`
12. `manage-project-board`
13. `view-management-dashboard`

## Incertezas reservadas para as entrevistas dos itens

- Autorização de membro para criar tarefa.
- Mutabilidade e unicidade do identificador de projeto.
- Recorte exato do painel apresentado ao membro.
- Tratamento de edição simultânea de tarefa.
- Origem e comportamento do cronômetro ativo citado como impedimento de arquivamento.
- Políticas detalhadas de senha, vínculo de redefinição e entrega de e-mail.

Essas incertezas não mudam inclusão, classificação, limite vertical, dependência ou ordem dos itens; serão tratadas somente na entrevista da Feature proprietária.

## Aprovação do catálogo

Pendente de aprovação explícita de Mário Tinelli.

## Progresso

13 Features catalogadas; nenhuma issue criada; nenhuma entrevista de item iniciada.

## Decisões de continuação

Nenhuma.

## Relações nativas

11 relações `blocks` planejadas; nenhuma publicada.

## Alterações do catálogo

Nenhuma.

## Gaps funcionais dos itens processados

Nenhum item foi processado.

## Resumo final

Pendente.

### Issues

Nenhuma.

### Relações

Nenhuma publicada.

### Artefatos

- `scope.md`
- `scope-state.json`
- 12 fontes normalizadas sob `sources/`

### Aprovações

Nenhuma.

### Validações

- Integridade das fontes: aprovada.
- Orientação do repositório: aprovada.
- Estado operacional: em validação.

### Próxima recomendação

Revisar e aprovar o catálogo completo e sua ordem antes de criar qualquer issue.

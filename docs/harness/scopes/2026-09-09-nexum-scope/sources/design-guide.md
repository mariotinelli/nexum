# Source: guia-de-design.html

- Source ID: `design-guide`
- Type: design HTML e anotações de produto
- Origin: C:\Users\maari\Downloads\nexum-scope\design\guia-de-design.html
- Original SHA-256: `801383f4687ff5c25486f5007341cf625910d75f7c6c9337d552ce3ec29baceb`
- Extraction: leitura estática integral do HTML UTF-8; texto extraído e scripts preservados como evidência inerte, sem execução.

## Extracted content

Guia de referência do MVP
Referência de design do MVP
16 telas responsivas, cada uma em um único HTML. Os estilos e scripts estão incorporados; o conteúdo inicial também pode ser lido sem executar JavaScript. Envie as telas desejadas e este guia à IA.
As telas são wireframes de baixa fidelidade, com dados ilustrativos. A identidade visual definitiva ainda não foi aprovada. Os comportamentos interativos precisam de JavaScript; autenticação e persistência de servidor são simuladas.
O mesmo arquivo se adapta a desktop e mobile. Links entre telas funcionam quando os HTMLs ficam juntos na mesma pasta. Cada tela pode ser visualizada individualmente, sem arquivos CSS ou JS adicionais.
Orientação para a IA
Use os HTMLs como referência de estrutura, hierarquia, navegação, campos e comportamento responsivo. Preserve o escopo abaixo e não acrescente funcionalidades. Na implementação Laravel/Livewire, utilize os componentes UI do Nexum indicados pelo responsável pelo projeto. Esses componentes Blade não estão incluídos neste pacote.
Telas e fluxos Login · F01
Autenticar o usuário ativo.
Acesso: Todos os perfis
Fluxo: Login → Painel. Recuperação → Login.
Regra: Usuários inativos não podem acessar. RN12.
Desktop: Formulário centralizado e uma única ação de entrada. Mobile: Coluna única, campos largos e teclado apropriado ao e-mail. Recuperar senha · F01
Solicitar instruções e redefinir a senha.
Acesso: Todos os perfis
Fluxo: Login → Recuperar → Confirmação → Redefinir → Login.
Regra: Resposta de envio não expõe se o e-mail está cadastrado.
Desktop: Formulário compacto; confirmação ocupa o mesmo contexto. Mobile: Mensagem de resultado ocupa a largura disponível. Painel · F13
Acompanhar progresso, atrasos e esforço.
Acesso: Gestor; membro com visão reduzida
Fluxo: Painel → Projeto → Tarefa.
Regra: Progresso por quantidade; realizadas por soma de apontamentos. RN14–RN15.
Desktop: Indicadores no topo; gráficos e projetos abaixo. Mobile: Indicadores, gráficos e projetos empilhados; navegação recolhida. Minhas tarefas · F07 · F09 · F14
Localizar responsabilidades e iniciar o trabalho.
Acesso: Usuário autenticado
Fluxo: Minhas tarefas → Tarefa → Cronômetro → Apontamentos.
Regra: Somente tarefas atribuídas ao usuário. Uma execução aberta por pessoa. RN05–RN06.
Desktop: Lista agrupada e ações rápidas; filtros antes do trabalho diário. Mobile: Cards por grupo; ações de toque abaixo dos dados; filtros em duas colunas. Projetos · F03
Consultar projetos acessíveis.
Acesso: Participantes; criação por gestor
Fluxo: Projetos → Novo projeto ou Detalhes do projeto.
Regra: Somente participantes podem acessar o projeto. RN02 e RN13.
Desktop: Cards com situação, gestor, progresso, prazo e horas. Mobile: Cards em coluna única; criar projeto respeita a permissão. Novo projeto · F03
Definir projeto, gestor e participantes.
Acesso: Gestor
Fluxo: Projetos → Novo projeto → Detalhes do projeto.
Regra: Todo projeto deve possuir um gestor. RN01.
Desktop: Formulário em duas colunas e participantes no mesmo fluxo. Mobile: Campos empilhados, papéis abaixo dos participantes e ação ao final. Detalhes do projeto · F03 · F13
Consultar resumo, participantes, tarefas e horas.
Acesso: Participantes
Fluxo: Projeto → Abas → Quadro / Tarefa / Editar projeto.
Regra: Arquivado fica disponível apenas para consulta. RN09.
Desktop: Resumo e indicadores lado a lado; abas para módulos do projeto. Mobile: Conteúdo empilhado e abas com quebra de linha. Editar projeto · F03
Atualizar dados, gestor, papéis e participantes.
Acesso: Gestor do projeto
Fluxo: Projeto → Editar → Salvar ou Arquivar.
Regra: Gestor obrigatório e projeto arquivado sem edição. RN01 e RN09.
Desktop: Dados e participantes em formulário; arquivamento separado. Mobile: Mesma sequência de campos, sem reduzir os alvos de toque. Quadro do projeto · F05 · F08
Organizar tarefas por situação.
Acesso: Participantes
Fluxo: Projeto → Quadro → Card → Tarefa.
Regra: Apenas transições permitidas pelo fluxo fixo.
Desktop: Quatro colunas de situação; ação no card substitui arrastar. Mobile: Colunas empilhadas, com contagem e rótulos completos. Tarefas · F04 · F14
Encontrar tarefas com busca, filtros e ordenação.
Acesso: Participantes
Fluxo: Tarefas → Nova tarefa ou Detalhes da tarefa.
Regra: Consulta limitada aos projetos acessíveis. RN02–RN05.
Desktop: Tabela com colunas essenciais e filtros recolhíveis. Mobile: Linhas viram cards com rótulos; paginação permanece acessível. Nova tarefa · F04–F06
Cadastrar uma entrega dentro de um projeto.
Acesso: Gestor; membro a validar
Fluxo: Lista ou Projeto → Nova tarefa → Detalhes.
Regra: Responsável deve participar do projeto; padrão Pendente e Média. RN03.
Desktop: Formulário em duas colunas, autor automático e estimativa em minutos. Mobile: Campos na ordem de preenchimento; validação junto ao formulário. Detalhes da tarefa · F04 · F09–F12
Executar, colaborar e consultar rastreabilidade.
Acesso: Participantes; edição por gestor ou responsável
Fluxo: Tarefa → Editar / Comentários / Horas / Histórico.
Regra: Conclusão registra data; reabertura remove. RN10–RN11.
Desktop: Conteúdo e detalhes lado a lado; abas para colaboração e registros. Mobile: Detalhes abaixo do conteúdo; cronômetro global no topo. Editar tarefa · F04–F06 · F12
Atualizar dados e situação da tarefa.
Acesso: Gestor ou responsável
Fluxo: Tarefa → Editar → Tarefa.
Regra: Somente responsável ou gestor atualiza; registrar alterações. RN04–RN05 e RN11.
Desktop: Campos originais preenchidos; situação limitada às transições válidas. Mobile: Uma coluna com mesma sequência e ações ao final. Apontamentos · F10
Consultar e registrar tempo nas tarefas.
Acesso: Participantes; editar somente próprios
Fluxo: Apontamentos → Registrar / Editar → Tarefa.
Regra: Tarefa obrigatória e duração maior que zero. RN07–RN08 e RN14.
Desktop: Tabela, total do período, filtros e formulário em modal. Mobile: Cards e modal ajustado à largura, com rolagem interna. Usuários · F02
Administrar pessoas e acesso ao sistema.
Acesso: Somente administrador
Fluxo: Usuários → Cadastrar / Editar / Ver projetos.
Regra: Somente administradores administram usuários; inativos não acessam. RN12.
Desktop: Tabela e formulários auxiliares em modal. Mobile: Cada usuário vira um card com ações identificadas. Perfil · F01
Atualizar dados pessoais e alterar senha.
Acesso: Usuário autenticado
Fluxo: Menu do usuário → Perfil → Salvar.
Regra: Alteração da própria senha; validação sem exposição de dados sensíveis.
Desktop: Dados pessoais e senha separados no mesmo formulário. Mobile: Campos empilhados e confirmação de senha explícita.
Escopo original completo Consultar requisitos e limites do MVP # Escopo Inicial do MVP de Gerenciamento de Projetos
## 1. Visão do produto
Criar um gerenciador de projetos que reúna planejamento, distribuição de tarefas, execução diária e apontamento de horas em uma única aplicação.
O produto deve permitir que gestores organizem e acompanhem projetos, enquanto os membros da equipe consultam suas responsabilidades, executam tarefas e registram o tempo trabalhado.
### Proposta de valor
> Planejar projetos, executar tarefas e acompanhar esforço e progresso no mesmo lugar, com simplicidade e rastreabilidade.
O produto será independente. Redmine e Rem Soft Gerenciador serão utilizados como referências funcionais, sem integração, sincronização ou dependência externa no MVP.
## 2. Referências funcionais
| Referência | Conceitos aproveitados |
| --- | --- |
| Redmine | Projetos, membros, tarefas, responsáveis, prioridades, prazos, comentários e histórico |
| Rem Soft Gerenciador | Minhas tarefas, cronômetro, apontamentos, execução diária e indicadores de horas |
O novo sistema não deve copiar limitações técnicas, IDs fixos, estruturas legadas ou regras específicas dos sistemas de referência.
## 3. Objetivos
- Centralizar projetos, tarefas, comentários e horas.
- Oferecer uma visão clara do trabalho de cada usuário.
- Permitir acompanhamento de progresso e atrasos.
- Registrar o histórico das principais alterações.
- Ser simples o suficiente para equipes pequenas começarem rapidamente.
- Funcionar bem em desktop e dispositivos móveis.
- Estabelecer uma base extensível para futuras funcionalidades.
## 4. Perfis de usuário
| Perfil | Responsabilidades |
| --- | --- |
| Administrador | Gerenciar usuários e configurações gerais |
| Gestor | Criar projetos, administrar membros e acompanhar tarefas |
| Membro | Executar tarefas, registrar horas e colaborar |
Um usuário pode ser gestor em um projeto e membro em outro.
## 5. Escopo funcional
### F01 - Autenticação
- Login por e-mail e senha.
- Logout.
- Recuperação de senha.
- Alteração da própria senha.
- Bloqueio de acesso para usuários inativos.
- Redirecionamento para o painel após o login.
### F02 - Usuários
- Listar usuários.
- Cadastrar usuário.
- Editar nome, e-mail e estado.
- Ativar ou desativar usuário.
- Definir ou remover acesso administrativo.
- Visualizar projetos dos quais o usuário participa.
Somente administradores podem administrar usuários.
### F03 - Projetos
- Criar projeto.
- Editar projeto.
- Arquivar e reativar projeto.
- Definir nome, identificador, descrição, gestor, data inicial e prazo.
- Adicionar e remover participantes.
- Definir o papel de cada participante.
- Visualizar progresso, tarefas e horas do projeto.
### F04 - Tarefas
Cada tarefa deve possuir:
| Campo | Obrigatório | Comportamento |
| --- | --- | --- |
| Projeto | Sim | Define o projeto ao qual a tarefa pertence |
| Título | Sim | Identificação principal da tarefa |
| Descrição | Não | Detalhamento do trabalho esperado |
| Situação | Sim | Inicia como Pendente |
| Prioridade | Sim | Inicia como Média |
| Autor | Sim | Preenchido automaticamente |
| Responsável | Não | Deve participar do projeto |
| Data inicial | Não | Data planejada para início |
| Prazo | Não | Data planejada para conclusão |
| Estimativa | Não | Quantidade prevista de minutos ou horas |
| Data de conclusão | Não | Preenchida automaticamente ao concluir |
Operações:
- Criar tarefa.
- Editar tarefa.
- Atribuir responsável.
- Alterar prioridade.
- Alterar situação.
- Concluir e reabrir tarefa.
- Arquivar tarefa.
- Consultar comentários, horas e histórico.
- Filtrar e ordenar tarefas.
### F05 - Fluxo de situações
Situações fixas do MVP:
- Pendente.
- Em andamento.
- Bloqueada.
- Concluída.
Transições permitidas:
| Origem | Destinos permitidos |
| --- | --- |
| Pendente | Em andamento ou Concluída |
| Em andamento | Pendente, Bloqueada ou Concluída |
| Bloqueada | Pendente, Em andamento ou Concluída |
| Concluída | Pendente ou Em andamento |
Ao concluir uma tarefa, o sistema registra a data de conclusão. Ao reabrir, o sistema remove essa data.
### F06 - Prioridades
Prioridades fixas do MVP:
- Baixa.
- Média.
- Alta.
- Urgente.
A prioridade padrão será Média.
### F07 - Minhas tarefas
A página deve apresentar as tarefas atribuídas ao usuário autenticado.
Seções:
- Em execução.
- Atrasadas.
- Para hoje.
- Próximas.
- Sem prazo.
- Concluídas recentemente.
Filtros:
- Projeto.
- Situação.
- Prioridade.
- Prazo.
- Busca textual.
- Apenas atrasadas.
A tela deve permitir iniciar, pausar e concluir tarefas rapidamente.
### F08 - Quadro de tarefas
Cada projeto terá um quadro dividido por situação:
- Pendente.
- Em andamento.
- Bloqueada.
- Concluída.
No MVP, a situação poderá ser alterada por uma ação no card. Drag-and-drop não é obrigatório.
Cada card deve mostrar:
- Título.
- Projeto, quando necessário.
- Responsável.
- Prioridade.
- Prazo.
- Estimativa.
- Horas realizadas.
- Indicador de atraso.
### F09 - Cronômetro
- Iniciar um cronômetro em uma tarefa.
- Pausar ou finalizar o cronômetro.
- Exibir o tempo decorrido.
- Impedir dois cronômetros ativos para o mesmo usuário.
- Exibir globalmente a tarefa em execução.
- Criar um apontamento quando o cronômetro for finalizado.
- Permitir descartar uma execução iniciada incorretamente.
- Manter o cronômetro correto após recarregar ou fechar a página.
### F10 - Apontamento manual
Cada apontamento terá:
- Tarefa.
- Usuário.
- Data.
- Duração.
- Descrição opcional.
- Origem manual ou cronômetro.
Operações:
- Criar apontamento.
- Editar o próprio apontamento.
- Excluir o próprio apontamento.
- Visualizar apontamentos da tarefa.
- Visualizar apontamentos do projeto.
No MVP, não haverá fluxo de aprovação de horas.
### F11 - Comentários
- Adicionar comentário em uma tarefa.
- Listar comentários em ordem cronológica.
- Exibir autor e horário.
- Editar o próprio comentário.
- Excluir o próprio comentário.
- Preservar formatação básica e quebras de linha.
Não haverá comentários privados nem menções no MVP.
### F12 - Histórico
O sistema deve registrar:
- Criação da tarefa.
- Mudança de situação.
- Mudança de responsável.
- Mudança de prioridade.
- Alteração do prazo.
- Alteração da estimativa.
- Conclusão e reabertura.
Cada evento deve identificar:
- Usuário responsável.
- Data e hora.
- Tipo da alteração.
- Valor anterior.
- Novo valor.
### F13 - Painel do gestor
Indicadores:
- Projetos ativos.
- Tarefas por situação.
- Tarefas atrasadas.
- Tarefas concluídas no período.
- Horas estimadas versus realizadas.
- Horas por membro.
- Progresso de cada projeto.
O progresso inicial será calculado por quantidade:
```text
tarefas concluídas / total de tarefas * 100
```
### F14 - Busca e filtros
- Busca textual por título da tarefa.
- Filtro por projeto.
- Filtro por responsável.
- Filtro por situação.
- Filtro por prioridade.
- Filtro por prazo.
- Ordenação por criação, prazo, prioridade ou atualização.
- Persistência dos filtros durante a sessão de navegação.
## 6. Regras de negócio
| ID | Regra |
| --- | --- |
| RN01 | Todo projeto deve possuir um gestor |
| RN02 | Apenas participantes podem acessar um projeto |
| RN03 | Apenas participantes podem ser responsáveis por tarefas do projeto |
| RN04 | Gestores podem administrar todas as tarefas dos seus projetos |
| RN05 | Membros podem atualizar tarefas atribuídas a eles |
| RN06 | Somente um cronômetro pode permanecer ativo por usuário |
| RN07 | Todo apontamento deve estar relacionado a uma tarefa |
| RN08 | A duração de um apontamento deve ser maior que zero |
| RN09 | Projetos arquivados ficam disponíveis apenas para consulta |
| RN10 | Tarefas concluídas registram automaticamente a data de conclusão |
| RN11 | Mudanças relevantes devem gerar histórico |
| RN12 | Usuários inativos não podem acessar a aplicação |
| RN13 | Usuários não podem acessar projetos dos quais não participam |
| RN14 | Horas realizadas são calculadas pela soma dos apontamentos |
| RN15 | Uma tarefa está atrasada quando não está concluída e seu prazo já passou |
## 7. Modelo de dados inicial
Tabelas principais:
```text
users
projects
project_user
tasks
time_entries
task_comments
task_events
```
Relacionamentos:
```text
User N:N Project
Project 1:N Task
User 1:N Task como autor
User 1:N Task como responsável
Task 1:N TimeEntry
Task 1:N TaskComment
Task 1:N TaskEvent
```
Enums iniciais:
```text
ProjectRole: Manager, Member
TaskStatus: Pending, InProgress, Blocked, Completed
TaskPriority: Low, Medium, High, Urgent
TimeEntrySource: Manual, Timer
```
Princípios do modelo:
- Utilizar chaves estrangeiras para os relacionamentos.
- Não duplicar nomes de projeto, usuário ou responsável nas tarefas.
- Armazenar duração preferencialmente em minutos inteiros.
- Centralizar situações e prioridades em enums de domínio.
- Registrar datas com timezone consistente.
- Criar índices para projeto, responsável, situação, prioridade e prazo.
- Garantir transacionalmente apenas um cronômetro aberto por usuário.
## 8. Páginas do MVP
| Página | Finalidade |
| --- | --- |
| Login | Autenticar o usuário |
| Recuperar senha | Solicitar redefinição de senha |
| Dashboard | Apresentar indicadores gerais |
| Minhas tarefas | Organizar o trabalho individual |
| Projetos | Listar projetos acessíveis |
| Novo projeto | Cadastrar projeto |
| Detalhes do projeto | Exibir resumo, membros, tarefas e horas |
| Editar projeto | Atualizar configurações e participantes |
| Quadro do projeto | Organizar tarefas por situação |
| Tarefas | Consultar tarefas com filtros |
| Nova tarefa | Cadastrar tarefa |
| Detalhes da tarefa | Consultar dados, comentários, horas e histórico |
| Editar tarefa | Atualizar tarefa |
| Apontamentos | Consultar e registrar horas |
| Usuários | Administrar usuários |
| Perfil | Atualizar dados pessoais e senha |
## 9. Diretrizes de arquitetura
O MVP deve ser desenvolvido como um monólito modular Laravel com Livewire.
Responsabilidades:
| Camada | Responsabilidade |
| --- | --- |
| Livewire | Estado da tela, validação, autorização da ação e apresentação |
| Actions e Workflows | Casos de uso, transições e operações com efeitos de negócio |
| Queries | Consultas de leitura reutilizáveis ou complexas |
| Models | Relacionamentos, casts, scopes e invariantes do modelo |
| Policies | Autorização por projeto e recurso |
| Events e listeners | Histórico e efeitos secundários desacoplados |
| Jobs | Operações demoradas ou futuras integrações externas |
Diretrizes:
- Manter os componentes Livewire pequenos e focados.
- Validar e autorizar toda ação no servidor.
- Não depender da visibilidade de botões para segurança.
- Centralizar as transições de situação.
- Utilizar transações para mudanças que envolvam múltiplos registros.
- Evitar microserviços no MVP.
- Não adicionar broadcasting sem necessidade validada.
- Escrever testes Pest para casos de uso, componentes e Policies.
## 10. Escopo do design system
### 10.1 Princípios visuais
- Clareza operacional.
- Alta densidade de informação sem poluição.
- Hierarquia visual forte.
- Ações principais facilmente identificáveis.
- Estados e prioridades reconhecíveis sem depender apenas de cores.
- Experiência consistente em desktop e mobile.
- Aparência profissional, objetiva e adequada ao uso diário prolongado.
### 10.2 Componentes necessários
- App shell.
- Sidebar responsiva.
- Navegação mobile.
- Cabeçalho de página.
- Breadcrumb.
- Botões e grupos de ações.
- Inputs, textarea, select e autocomplete.
- Datepicker e seletor de duração.
- Checkbox, radio e switch.
- Card de projeto.
- Card de tarefa.
- Coluna de quadro.
- Tabela responsiva.
- Badge de situação.
- Badge de prioridade.
- Avatar e grupo de avatares.
- Barra de progresso.
- Cronômetro global.
- Modal e drawer.
- Dropdown de ações.
- Tabs.
- Filtros e campo de busca.
- Paginação.
- Timeline de histórico.
- Lista de comentários.
- Empty state.
- Skeleton.
- Toast.
- Alertas de confirmação e erro.
- Gráficos básicos.
### 10.3 Estados dos componentes
Cada componente interativo deve definir:
- Default.
- Hover.
- Focus.
- Active.
- Disabled.
- Loading.
- Error.
- Success.
- Empty, quando aplicável.
### 10.4 Responsividade
| Faixa | Comportamento |
| --- | --- |
| Mobile | Navegação recolhida, cards, drawers e ações adequadas para toque |
| Tablet | Layout intermediário e tabelas adaptadas |
| Desktop | Sidebar, tabelas completas e painéis laterais |
### 10.5 Acessibilidade
- Contraste mínimo WCAG AA.
- Navegação por teclado.
- Focus visível.
- Labels associados aos campos.
- Mensagens de erro descritivas.
- Ícones acompanhados por texto ou nome acessível.
- Situações não representadas exclusivamente por cor.
- Áreas clicáveis adequadas para telas de toque.
- Hierarquia semântica de títulos.
- Respeito às preferências de redução de movimento.
## 11. Requisitos não funcionais
- Interface responsiva.
- Autorização validada no servidor.
- Senhas protegidas por hash.
- Testes automatizados dos fluxos críticos.
- Paginação nas listagens.
- Logs de erros sem dados sensíveis.
- Transações em alterações relacionadas.
- Índices para filtros frequentes.
- Datas armazenadas com timezone consistente.
- Tempos armazenados preferencialmente em minutos.
- Bom funcionamento sem serviços externos.
- Componentes preparados para tradução, mesmo que o MVP utilize apenas português.
- Estados de loading, vazio, erro e indisponibilidade tratados nas telas principais.
## 12. Fora do escopo
- Integração com Redmine, Jira ou GitLab.
- Importação do sistema legado.
- Code Review e QA.
- Suporte e SLA.
- Gestão de freelancers.
- Sprints e backlog Scrum.
- Gantt e roadmap.
- Campos personalizados.
- Workflow configurável.
- Subprojetos.
- Dependências e relações entre tarefas.
- Arquivos e anexos.
- Notificações por e-mail ou Discord.
- Notificações em tempo real.
- Aprovação de apontamentos.
- Faturamento e centros de custo.
- Aplicativo mobile nativo.
- API pública.
- Sincronização com sistemas externos.
## 13. Critérios de sucesso
O MVP estará apto para piloto quando:
- Um administrador conseguir cadastrar usuários.
- Um gestor conseguir criar um projeto e adicionar membros.
- Um membro conseguir criar ou receber uma tarefa.
- Uma tarefa conseguir percorrer todo o fluxo de situações.
- O usuário conseguir iniciar e finalizar um cronômetro.
- O sistema impedir dois cronômetros simultâneos.
- Horas manuais e automáticas aparecerem corretamente na tarefa.
- Comentários e histórico registrarem autoria e horário.
- O gestor conseguir identificar progresso e atrasos.
- Usuários não conseguirem acessar projetos alheios.
- As operações principais funcionarem em desktop e mobile.
- O uso do sistema não depender de Redmine ou de outro serviço externo.
## 14. Épicos e features para desenvolvimento
| Épico | Features |
| --- | --- |
| Fundação | Autenticação, layout, navegação e autorização |
| Usuários | Cadastro, edição, ativação, desativação e perfil |
| Projetos | CRUD, arquivamento, participantes e papéis |
| Tarefas | CRUD, atribuição, situações, prioridades e prazos |
| Execução | Minhas tarefas, cronômetro e apontamentos |
| Colaboração | Comentários e histórico |
| Gestão | Dashboard, quadro, filtros e indicadores |
| Qualidade | Responsividade, acessibilidade, segurança e testes |
## 15. Ordem recomendada de desenvolvimento
1. Fundação, autenticação e layout.
2. Usuários e autorização.
3. Projetos e participantes.
4. Tarefas e fluxo de situações.
5. Minhas tarefas.
6. Cronômetro e apontamentos.
7. Comentários e histórico.
8. Quadro e dashboard.
9. Responsividade e acessibilidade.
10. Estabilização para o piloto.
Cada etapa deve entregar um fluxo vertical utilizável e testável, evitando construir todas as camadas técnicas antes de disponibilizar valor funcional.
## 16. Estimativa relativa
| Entrega | Porte relativo |
| --- | --- |
| Fundação, autenticação e autorização | Médio |
| Projetos e membros | Pequeno |
| Tarefas e transições | Médio |
| Minhas tarefas e filtros | Médio |
| Apontamento manual e cronômetro | Médio |
| Comentários e histórico | Pequeno |
| Quadro e indicadores | Médio |
| Estabilização para piloto | Médio |
O MVP completo é considerado de porte geral médio para grande, mas pode ser dividido em entregas verticais menores.
## 17. Riscos e mitigação
| Risco | Mitigação |
| --- | --- |
| Crescimento do escopo até reproduzir o Redmine | Manter o fora do escopo explícito e validar novas ideias após o piloto |
| Reintrodução de regras específicas do legado | Implementar apenas regras confirmadas como necessárias |
| Situações inconsistentes | Utilizar enum canônico e operação única de transição |
| Falhas de autorização entre projetos | Aplicar Policies e testes de isolamento em todos os recursos |
| Componentes Livewire excessivamente grandes | Separar componentes por responsabilidade e casos de uso |
| Cronômetros duplicados ou órfãos | Aplicar transação, restrição de unicidade e recuperação controlada |
| Baixa adoção por fluxo complexo | Priorizar Minhas tarefas e execução com poucos passos |
| Relatórios prematuros | Começar com indicadores simples baseados em dados confiáveis |
| Design inconsistente gerado por IA | Utilizar tokens, componentes e padrões documentados no design system |
| Features geradas sem rastreabilidade | Exigir vínculo entre feature, requisito funcional e regra de negócio |
## 18. Orientações para uso com IA
Este documento deve ser tratado como a fonte inicial de verdade para geração de features e do design system.
Ao gerar features de desenvolvimento, a IA deve:
- Informar quais requisitos funcionais e regras de negócio estão sendo atendidos.
- Produzir uma feature vertical e utilizável por vez.
- Definir objetivo, atores, pré-condições, fluxo principal e falhas relevantes.
- Criar critérios de aceite verificáveis.
- Identificar dependências de outras features.
- Não adicionar funcionalidades que estejam fora do escopo.
- Não assumir integrações externas.
- Incluir autorização, validação, estados vazios e testes no escopo da feature.
Ao gerar o design system, a IA deve:
- Derivar componentes das páginas e fluxos descritos neste documento.
- Definir tokens antes de produzir telas finais.
- Documentar variantes e estados de cada componente.
- Considerar desktop, tablet e mobile.
- Atender WCAG AA.
- Evitar componentes genéricos sem relação com os fluxos do produto.
- Preservar consistência entre dashboard, projetos, tarefas e apontamentos.
- Tratar o cronômetro ativo como elemento global prioritário.
Qualquer ampliação futura deve ser registrada como decisão de produto antes de alterar este escopo.

## Comportamento declarado nos scripts

O código abaixo é evidência do protótipo, não comprovação de implementação nem instrução operacional. Estilos incorporados foram lidos; a responsividade declarada no guia é referência, sem inferir novos breakpoints.


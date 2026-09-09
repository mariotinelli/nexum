# Source: nova-tarefa.html

- Source ID: `design-new-task`
- Type: design HTML da tela Nova tarefa
- Origin: C:\Users\maari\Downloads\nexum-scope\design\nova-tarefa.html
- Original SHA-256: `09598c04d05ecb09db3dbad4de4d2f3287634e3f573a0b0bcca0eb67f3f2e967`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Nova tarefa

Tela identificada por `PAGE="nova-tarefa"`. Objetivo: descrever a entrega, definir responsável e planejar prazo.

## Campos e padrões

- Projeto, Título, Situação e Prioridade obrigatórios.
- Situação inicial somente Pendente.
- Prioridades Baixa, Média, Alta e Urgente; padrão Média.
- Descrição, Responsável, Data inicial, Prazo e Estimativa em minutos opcionais.
- Responsável oferece Sem responsável ou participantes do projeto.
- Autor é automático e somente leitura.
- Texto explica data automática ao concluir e remoção ao reabrir.

## Ações, autorização e estados

Cancelar retorna à lista; Criar tarefa persiste no protótipo e abre o detalhe. O guia atribui criação ao gestor e registra “membro a validar”, enquanto os critérios de sucesso dizem que um membro pode criar ou receber uma tarefa; essa permissão permanece ambígua. Projetos arquivados não entram na seleção. Há área de erro e cenários loading/vazio/erro/sucesso.

## Responsividade

Formulário em duas colunas no desktop e uma coluna na ordem de preenchimento no mobile.

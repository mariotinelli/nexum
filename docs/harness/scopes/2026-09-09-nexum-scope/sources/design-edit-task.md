# Source: editar-tarefa.html

- Source ID: `design-edit-task`
- Type: design HTML da tela Editar tarefa
- Origin: C:\Users\maari\Downloads\nexum-scope\design\editar-tarefa.html
- Original SHA-256: `adce7137a9fb397ce56f4b763d5e2f37c8e9a0ee6ece3cc99b68461db8b7c027`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Editar tarefa

Tela identificada por `PAGE="editar-tarefa"`, com valores existentes preenchidos.

## Campos e ações

Projeto, Título, Situação e Prioridade obrigatórios; Descrição, Responsável, Data inicial, Prazo e Estimativa opcionais; Autor automático. A situação lista o valor atual e somente destinos permitidos. Responsável é restrito a participantes do projeto. Ações Cancelar e Salvar alterações.

## Autorização, histórico e estados

O protótipo permite editar se o projeto está ativo e o usuário é gestor ou responsável. Sem permissão, mostra estado de consulta e link para a tarefa. Mudanças de situação, responsável, prioridade, prazo e estimativa são candidatas a evento de histórico; conclusão define data e reabertura remove. Cenários genéricos incluem loading/vazio/erro/sucesso.

## Responsividade

Desktop organiza campos em duas colunas; mobile mantém a mesma sequência em uma coluna com ações ao final. A fonte não define conflitos de edição simultânea.

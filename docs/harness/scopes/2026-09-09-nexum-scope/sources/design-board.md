# Source: quadro-projeto.html

- Source ID: `design-board`
- Type: design HTML da tela Quadro do projeto
- Origin: C:\Users\maari\Downloads\nexum-scope\design\quadro-projeto.html
- Original SHA-256: `1e6f84992ed4d14aa2ba45568a8719417a6b02c70d984e59bb81dc1c8318ec0d`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Quadro do projeto

Tela identificada por `PAGE="quadro-projeto"`. Cabeçalho identifica o projeto e orienta alterar a situação diretamente no card, com ação Nova tarefa quando o projeto está ativo.

## Colunas e cards

Quatro colunas fixas: Pendente, Em andamento, Bloqueada e Concluída, cada uma com contagem e estado “Nenhuma tarefa”. Cards mostram título com link, responsável, prioridade, prazo/atraso, estimativa e horas realizadas. Usuário autorizado recebe select de situação com valor atual e destinos permitidos.

## Regras e estados

Não há drag-and-drop; a mudança ocorre pelo controle no card. Projeto arquivado mostra aviso e remove mutações. Consulta limitada a participantes; edição segue gestor/responsável. Estado vazio remove cards; loading/erro/sucesso são previstos.

## Responsividade

Desktop usa quatro colunas; mobile empilha as colunas com contagem e rótulos completos. Situação e prioridade não dependem apenas da posição/cor, pois têm texto.

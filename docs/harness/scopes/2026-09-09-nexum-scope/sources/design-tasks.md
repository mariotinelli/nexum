# Source: tarefas.html

- Source ID: `design-tasks`
- Type: design HTML da tela Tarefas
- Origin: C:\Users\maari\Downloads\nexum-scope\design\tarefas.html
- Original SHA-256: `958027e41eb2543125e745c457fae750741bf4c45336ea2bbb148f5ef7ab154e`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Tarefas

Tela identificada por `PAGE="tarefas"`. Consulta tarefas dos projetos em que o usuário participa e oferece Nova tarefa.

## Busca, filtros e ordenação

Busca por texto; filtros Projeto, Situação, Prioridade, Responsável, Prazo até e Apenas atrasadas; ordenação por Criação, Prazo, Prioridade ou Atualização. Ações Aplicar filtros e Limpar. O código declara persistência dos filtros em `sessionStorage` por página.

## Resultado

Tabela com Tarefa, Situação, Responsável, Prazo e Prioridade. O título abre detalhes; atraso aparece junto ao prazo. Paginação mostra contagem e habilita/desabilita Anterior/Próxima. Estado vazio diz que nenhum registro foi encontrado e permite limpar filtros.

## Regras, estados e responsividade

Somente tarefas não arquivadas de projetos acessíveis entram na consulta. Cenários: padrão, carregando, vazio, erro e sucesso. Em mobile, tabela vira cards com rótulos e filtros se reorganizam; paginação continua acessível. A fonte não especifica combinação lógica além dos filtros simultâneos demonstrados.

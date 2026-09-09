# Source: projetos.html

- Source ID: `design-projects`
- Type: design HTML da tela Projetos
- Origin: C:\Users\maari\Downloads\nexum-scope\design\projetos.html
- Original SHA-256: `6370083f10a0dc678771a44d6315eeaf4978b43d79b3d4331213e5ffe4951fee`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Projetos

Tela identificada por `PAGE="projetos"`. Lista “Projetos dos quais você participa”, com ação Novo projeto e filtro Exibir: Todos, Ativos ou Arquivados.

## Conteúdo e navegação

Cada card mostra identificador, estado, nome, gestor, contagem de tarefas concluídas, percentual de progresso, prazo e horas realizadas. Abrir projeto leva aos detalhes. O estado inicial contém um projeto ativo e paginação com contagem; Anterior/Próxima ficam desabilitados quando não aplicáveis.

## Regras e variações declaradas

A função de acessibilidade filtra projetos pela participação do usuário. A ação de criar projeto é destinada ao gestor; o protótipo também varia navegação por `perfil=admin|gestor|membro`. Estados previstos: padrão, carregando, vazio, erro e sucesso; projeto arquivado permanece consultável.

## Responsividade

Desktop apresenta cards com dados operacionais. Mobile usa uma coluna, menu recolhido e mantém os alvos de ação. A permissão de criação deve ser confirmada no servidor na implementação; o HTML apenas a simula.

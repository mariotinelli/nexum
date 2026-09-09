# Source: usuarios.html

- Source ID: `design-users`
- Type: design HTML da tela Usuários
- Origin: C:\Users\maari\Downloads\nexum-scope\design\usuarios.html
- Original SHA-256: `900da2a517fdd275860861d8e4a81ad005a1b480372a3ee38999adc698d12814`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Usuários

Tela identificada por `PAGE="usuarios"` e perfil padrão `admin`. O shell inclui a entrada Usuários e identifica a pessoa como Administrador. Objetivo visível: gerenciar cadastros, acesso administrativo e situação.

## Listagem e ações

Tabela com Nome/e-mail, Estado, Acesso e Ações. Dados ilustram usuário Ativo/Administrador e usuário Ativo/Padrão. Ações: Cadastrar usuário, Editar e Projetos. Paginação mostra contagem e botões Anterior/Próxima desabilitados quando não há outra página.

## Formulário modal declarado

Cadastro/edição abre modal com Nome e E-mail obrigatórios, Estado (`Ativo`/`Inativo`) e checkbox Acesso administrativo, com Salvar usuário. Projetos abre modal com Projeto e Papel ou informa ausência de participação. Apenas `role=admin` aciona esses controles no protótipo.

## Estados, responsividade e acessibilidade

Prevê estados loading, vazio, erro e sucesso. Em mobile, linhas viram cards e ações permanecem nomeadas; menu lateral vira menu móvel. Modal usa título associado, restaura foco e tem ações Fechar/Cancelar. A autorização real no servidor não é demonstrada.

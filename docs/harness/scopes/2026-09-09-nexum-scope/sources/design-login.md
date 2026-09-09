# Source: login.html

- Source ID: `design-login`
- Type: design HTML da tela Login
- Origin: C:\Users\maari\Downloads\nexum-scope\design\login.html
- Original SHA-256: `6d91c42bde1f3f17821f4b91f9e135ce9309d23da2c8d66cf90df6d969be7546`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Login

Tela identificada por `<title>Login · Wireframes do MVP</title>` e `PAGE="login"`. O estado inicial mostra marca textual “Gerenciador de projetos”, título Entrar e a orientação “Acesse seus projetos e organize seu trabalho”.

## Campos e ações

- E-mail: `type=email`, obrigatório.
- Senha: `type=password`, obrigatória.
- Ação primária Entrar.
- Link Esqueci minha senha para `recuperar-senha.html`.
- Região de erro com `role=alert` e toast com `role=status`/`aria-live=polite`.

## Estados e comportamento declarados

O protótipo aceita perfil por query string e cenários `padrao`, `carregando`, `vazio`, `erro`, `sucesso` e, para autenticação, `inativo`. Erro informa credenciais inválidas; inativo orienta solicitar reativação. O fluxo simulado redireciona ao painel após autenticação. O próprio wireframe alerta que autenticação e persistência são simuladas e que não se deve usar senha real.

## Responsividade e acessibilidade

Formulário centralizado com largura limitada; em viewport estreito reduz margens mantendo coluna única. Labels são associados aos campos, há foco visível e mensagem de erro acessível. A identidade visual é ilustrativa e não definitiva.

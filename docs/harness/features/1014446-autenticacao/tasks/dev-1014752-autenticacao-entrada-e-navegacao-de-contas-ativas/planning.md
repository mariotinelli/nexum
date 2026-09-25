# Planejamento técnico — DEV #1014752

## Identidade e fontes

- Filha canônica: Redmine `#1014752`, `[DEV] [WEB] [PUBLICO] Autenticação - Entrada e navegação de contas ativas`.
- Pai: Feature `#1014446 — Autenticação`.
- Fonte funcional local: `task.md` da filha e `feature.md` do pai, alinhados com o readback sanitizado do Redmine e com a reconciliação legada concluída do `project-slices`.
- Repositório inspecionado no commit `5ea83a7243ac2560cf7ececc24b5732f23249d5b` e no fingerprint persistido em `.flow/plan-issue.json`.
- Regras determinantes: URLs por área de usuário, `/admin/login` exclusivo da área administrativa, `/cliente/*` para clientes, recuperação de senha compartilhada fora dos prefixos e testes Pest espelhando cada classe com comportamento.

## Objetivo

Entregar entrada autenticada para todas as contas ativas pelos pontos de acesso de suas áreas, recusar contas inativas inclusive nas sessões já abertas, retirar o cadastro público e manter navegação responsiva, acessível e limitada às capacidades autorizadas no servidor. O trabalho deve preservar perfil, papéis e permissões existentes e direcionar cada usuário ao painel já disponível para sua área.

## Estado atual

- `App\Livewire\Admin\Auth\Login` já valida e-mail e senha, aplica rate limit, aceita Lembrar-me, regenera a sessão e restringe o destino pretendido à área administrativa.
- O login administrativo aceita `Admin`, `User` e `SupportRemSoft`; `Customer` é recusado e ainda não possui entrada em `/cliente/login`.
- `/login` redireciona para `/admin/login`, contrariando a regra local que proíbe rotas de área na raiz.
- `GET /register` e `POST /register` continuam publicados por `RegisteredUserController`.
- `User` usa exclusão lógica; isso impede a resolução normal de contas desativadas, mas não há cobertura dedicada que prove o bloqueio da próxima requisição HTTP e da próxima interação Livewire em sessões previamente abertas.
- `SidebarMenuBuilder` já separa o menu base do cliente, o menu administrativo e o menu de suporte, filtrando itens por autorização. As rotas administrativas também usam middleware e policies.
- A tela de login já possui layout responsivo, labels, Lembrar-me, recuperação de acesso e estado de carregamento. O controle de revelar senha, porém, usa ícones clicáveis sem semântica de botão, nome acessível ou estado anunciado.

## Escopo

Inclui os logins das áreas administrativa e de cliente, validação e rate limit existentes, mensagem de orientação para conta inativa, destinos seguros, remoção das rotas públicas de cadastro, bloqueio da próxima ação de sessões desativadas, navegação filtrada e a experiência acessível/responsiva de login e navegação. Inclui testes de servidor, Livewire e navegador para os critérios desta filha.

Não inclui criar ou administrar contas, recuperar ou redefinir senha, editar perfil, implementar capacidades de projetos/indicadores, definir os 30 dias de Lembrar-me ou alterar o isolamento do logout entre navegadores; os dois últimos comportamentos pertencem à DEV seguinte. A entrada visual para recuperação é preservada, sem ampliar o fluxo nesta entrega.

## Arquitetura

- Manter Livewire class-based para os formulários e extrair o comportamento comum de autenticação para uma unidade compartilhada, deixando componentes finos por área responsáveis pelos perfis aceitos, texto contextual e destino seguro.
- Publicar entradas somente em grupos nomeados e prefixados (`admin` e `cliente`); não manter alias público em `/login`.
- Reutilizar `Auth`, `RateLimiter`, regeneração de sessão e redirecionamento por rota nomeada. A validação de destino pretendido deve permanecer restrita ao prefixo da área atual.
- Tratar conta desativada com uma verificação explícita que não exponha senha nem detalhes além da orientação funcional exigida, e aplicar a barreira de conta ativa no ciclo HTTP que também envolve requisições Livewire autenticadas.
- Preservar `SidebarMenuBuilder`, middleware de área e policies como camadas complementares: ocultar itens não substitui autorização de rota.
- Reutilizar `x-ui.*` e Tailwind existentes. A melhoria do campo de senha deve ocorrer no componente compartilhado com semântica nativa, foco visível, alvo de toque e suporte a teclado, evitando JavaScript paralelo ao Alpine já adotado.

## Estratégia

Executar em quatro fases sequenciais e seguras para commit. Cada fase começa por testes que expressem o comportamento observável, implementa somente o necessário para fazê-los passar e roda a verificação focada correspondente. O fechamento executa `php ./vendor/bin/pest --parallel --tia --configuration=phpunit-ci.xml`, definido pelo desenvolvedor como o gate válido desta DEV.

## Baseline

- O gate `php ./vendor/bin/pest --parallel --tia --configuration=phpunit-ci.xml` foi executado diretamente com o PHP local e terminou verde, com código de saída `0`, sobre a evidência inspecionada atual.
- Por decisão explícita do desenvolvedor em 25/09/2026, esse é o único gate do planejamento.

## Riscos

- A mensagem específica de conta inativa pode facilitar enumeração de contas. Ela deve ser emitida apenas no caso funcional exigido e nunca revelar senha, hash ou outros dados da conta.
- Remover `/login` e `/register` altera URLs legadas; testes de rotas devem tornar a indisponibilidade intencional e impedir reintrodução acidental.
- A invalidação de sessão precisa alcançar requisições Livewire, não apenas navegações completas. Cobertura exclusivamente HTTP deixaria uma lacuna no aceite.
- Alterar `x-ui.input.password` afeta outras telas que reutilizam o componente. A mudança deve manter a API atual e receber verificação visual/navegacional nas telas diretamente impactadas.
- Menu oculto não protege acesso direto. Qualquer discrepância encontrada entre definição de menu, middleware e policy deve ser corrigida no servidor antes de considerar a fase aceita.

## Fase 1 — Entradas por área e cadastro público indisponível

### Objetivo

Permitir login de contas ativas de todos os perfis pelo endereço correto de sua área e retirar todos os pontos públicos de cadastro e o alias de login na raiz.

### Dependências

Baseline verde da suíte Pest; enum `TypeUsers`; painel base `dashboard`; painel `admin.dashboard`; componente administrativo e rotas de autenticação existentes.

### Mudanças esperadas

- Caracterizar primeiro as rotas aceitas e recusadas: `/admin/login` para `Admin`, `User` e `SupportRemSoft`; `/cliente/login` para `Customer`; ausência de `/login`; `GET` e `POST /register` indisponíveis.
- Extrair o fluxo comum do login atual e manter componentes/adaptadores por área com listas de perfis e destinos explícitos.
- Restringir o `url.intended` ao prefixo da área correspondente e usar o painel da própria área como fallback.
- Preservar validação, rate limit, Lembrar-me, regeneração de sessão e link para recuperação compartilhada.

### Arquivos prováveis

- `routes/admin.php`
- `routes/auth.php`
- `routes/customer.php`
- `routes/web.php`
- `app/Livewire/Admin/Auth/Login.php`
- `app/Livewire/Customer/Auth/Login.php`
- unidade compartilhada sob `app/Livewire/Auth/`
- `resources/views/livewire/auth/login.blade.php`
- `tests/Feature/Livewire/Admin/Auth/LoginTest.php`
- `tests/Feature/Livewire/Customer/Auth/LoginTest.php`
- `tests/Feature/Routes/AdminAuthenticationRoutesTest.php`
- teste de rotas da área de cliente espelhando a convenção mais próxima
- `tests/Feature/Http/Controllers/Auth/RegisteredUserControllerTest.php`

### Limites

Não remover o fluxo administrativo de criação de usuários, não alterar papéis ou permissões, não implementar recuperação de senha e não definir a duração do Lembrar-me. Evitar excluir classes ou testes legados sem confirmação; a indisponibilidade pública deve ser alcançada pelas rotas e comprovada por teste.

### Estratégia

Escrever testes de rota e de componente para cada matriz perfil/área, incluindo destino pretendido interno e externo. Implementar a menor abstração compartilhada que elimine duplicação do fluxo sensível, mantendo as decisões de área nas classes concretas. Atualizar a view compartilhada apenas para receber o contexto textual da área.

### Aceite

- Cada perfil ativo autentica somente pela entrada compatível e chega ao painel existente sem alteração de tipo, papel ou permissões.
- Cliente não entra pela área administrativa; perfis administrativos não entram pela área de cliente.
- Destino pretendido fora da área é ignorado.
- `/login`, `GET /register` e `POST /register` não oferecem entrada ou criação de conta.
- Validação, credenciais inválidas e rate limit continuam funcionando em português.

### Verificação focada

Executar com o PHP local os testes dedicados dos dois componentes de login, os testes de rotas administrativas e de cliente e o teste que prova a indisponibilidade do cadastro público.

## Fase 2 — Contas inativas e revogação na próxima ação

### Objetivo

Recusar novo login de conta desativada com orientação de reativação e bloquear, na próxima ação, cada sessão que já estava autenticada quando a conta foi desativada.

### Dependências

Fase 1 concluída; exclusão lógica de `User`; autenticação web por sessão; endpoints HTTP e componentes Livewire autenticados existentes.

### Mudanças esperadas

- Adicionar testes para conta inativa com credenciais corretas e para não autenticação após desativação.
- Introduzir uma barreira dedicada de conta ativa no pipeline autenticado, invalidando a sessão local e redirecionando para a entrada apropriada quando o usuário persistido estiver desativado.
- Cobrir duas sessões independentes da mesma conta e demonstrar que cada uma é bloqueada somente quando realiza sua próxima ação.
- Cobrir uma requisição HTTP comum e uma interação Livewire após a desativação.
- Manter a mensagem genérica para credenciais incorretas e não registrar nem retornar senha ou hash.

### Arquivos prováveis

- `app/Livewire/Admin/Auth/Login.php`
- `app/Livewire/Customer/Auth/Login.php`
- unidade compartilhada sob `app/Livewire/Auth/`
- novo middleware sob `app/Http/Middleware/`
- `bootstrap/app.php`
- `routes/web.php`
- `routes/admin.php`
- `routes/customer.php`
- testes dedicados espelhados em `tests/Feature/Http/Middleware/`
- testes dos componentes em `tests/Feature/Livewire/**/Auth/`

### Limites

Não implementar a tela ou ação administrativa que desativa a conta; os testes podem usar factory e exclusão lógica como pré-condição. Não encerrar outras sessões por logout voluntário nem alterar a política temporal de Lembrar-me.

### Estratégia

Começar pelos cenários de regressão de login e pelas duas formas de próxima ação. Criar o middleware por gerador Artisan e registrá-lo no ponto mais estreito que cubra todas as rotas autenticadas e o endpoint de atualização Livewire. Ao bloquear, efetuar logout da sessão corrente, invalidar/regenerar o token CSRF conforme as APIs do guard e redirecionar sem loop para a entrada da área.

### Aceite

- Conta desativada não autentica novamente e recebe orientação para solicitar reativação quando apresenta credenciais válidas.
- Credenciais inválidas continuam com mensagem genérica.
- Duas sessões abertas deixam de acessar o sistema independentemente na primeira ação posterior à desativação.
- O bloqueio ocorre tanto em navegação HTTP quanto em chamada Livewire sem recarga completa.
- Nenhuma sessão de outro usuário é afetada.

### Verificação focada

Executar com o PHP local o teste dedicado do middleware, os testes de login inativo das duas áreas e os testes Livewire/HTTP que simulam sessões previamente abertas.

## Fase 3 — Navegação autorizada por perfil

### Objetivo

Consolidar que a navegação autenticada mostra somente capacidades entregues e permitidas e que o servidor recusa acessos diretos não autorizados.

### Dependências

Fases 1 e 2 concluídas; `SidebarMenuBuilder`, definições de menu, `EnsureUserCanAccessAdminArea` e policies existentes.

### Mudanças esperadas

- Ampliar a matriz de testes do menu para todos os perfis e permissões relevantes, sem antecipar capacidades de outras Features.
- Conferir correspondência entre cada item exibido, rota nomeada e autorização de servidor.
- Adicionar regressões de acesso direto entre áreas e a rotas administrativas protegidas.
- Ajustar apenas discrepâncias comprovadas entre menu e autorização, preservando as definições existentes que já atendem ao requisito.

### Arquivos prováveis

- `app/Support/Navigation/SidebarMenuBuilder.php`
- definições sob `app/Support/Navigation/Definitions/`
- `app/Http/Middleware/EnsureUserCanAccessAdminArea.php`
- `routes/admin.php`
- `routes/customer.php`
- `tests/Feature/Support/Navigation/SidebarMenuBuilderTest.php`
- `tests/Feature/Http/Middleware/EnsureUserCanAccessAdminAreaTest.php`
- testes de rota das áreas administrativa e de cliente

### Limites

Não criar páginas, projetos, indicadores ou permissões novas. Não considerar ocultação de menu como autorização suficiente e não ampliar acesso para fazer um link funcionar.

### Estratégia

Montar uma tabela de casos em Pest para cliente, usuário interno, administrador e suporte, cobrindo permissões presentes e ausentes. Para cada capacidade exibida, testar também o endpoint protegido; para cada perfil incompatível, testar o acesso direto recusado ou redirecionado conforme a convenção atual.

### Aceite

- Cliente vê somente o painel base disponível.
- Usuário interno, administrador e suporte veem apenas itens definidos e autorizados para seu perfil.
- Login não concede papel, permissão, participação em projeto ou acesso administrativo adicional.
- URLs diretas de outra área e ações sem permissionamento são bloqueadas no servidor.

### Verificação focada

Executar com o PHP local `SidebarMenuBuilderTest`, o teste dedicado do middleware administrativo e os testes de rotas/autorização alterados nesta fase.

## Fase 4 — Acessibilidade e responsividade do login e da navegação

### Objetivo

Completar a experiência de login e navegação em desktop e mobile com semântica, teclado, foco, feedback e alvos de interação adequados.

### Dependências

Fases 1 a 3 concluídas; componentes `x-ui.*`, Alpine, Tailwind e infraestrutura de browser tests do Pest já instalados.

### Mudanças esperadas

- Transformar o revelar/ocultar senha em botão acessível por teclado, com nome e estado anunciáveis, foco visível e alvo de toque adequado, preservando o binding do input.
- Garantir associação de labels, ordem de teclado, hierarquia semântica e mensagens perceptíveis nos logins das duas áreas.
- Confirmar que o botão Entrar anuncia e exibe carregamento durante `login`, sem permitir envio duplicado.
- Validar contraste das variantes usadas, redução de movimento e comportamento responsivo do layout e dos menus sem introduzir estilos paralelos aos componentes existentes.
- Expandir browser tests para interação real com o controle de senha, foco/teclado, desktop, mobile e ausência de erros JavaScript.

### Arquivos prováveis

- `resources/views/components/ui/input/password.blade.php`
- `resources/views/components/ui/input.blade.php`
- `resources/views/components/ui/button.blade.php`
- `resources/views/livewire/auth/login.blade.php`
- `resources/views/layouts/guest.blade.php`
- views/componentes da navegação somente se um defeito for comprovado
- `tests/Browser/Livewire/Auth/LoginBrowserTest.php`
- browser test da área de cliente ou matriz equivalente no arquivo dedicado
- testes de renderização dos componentes Livewire afetados

### Limites

Não redesenhar a identidade visual, não criar componentes alternativos aos `x-ui.*` existentes e não implementar o fluxo de recuperação. Mudanças no componente de senha devem ser compatíveis com todos os consumidores atuais.

### Estratégia

Escrever primeiro browser tests para o comportamento JavaScript e testes Livewire/HTML para atributos estáveis. Implementar a semântica com elemento `button`, atributos ARIA dinâmicos e classes Tailwind alinhadas ao catálogo existente. Validar ambas as áreas em viewport desktop e mobile, incluindo navegação por teclado e console limpo.

### Aceite

- Campos têm labels associados, erros descritivos e foco perceptível; a sequência de teclado alcança todos os controles na ordem esperada.
- Revelar senha funciona por clique e teclado, anuncia seu propósito/estado e não submete o formulário.
- Entrar apresenta carregamento perceptível e evita envio duplicado; erro e sucesso produzem retorno observável.
- Login e navegação permanecem utilizáveis em desktop e mobile, com alvos de toque, contraste e redução de movimento compatíveis com os critérios da Feature.
- Não há erro JavaScript nos fluxos cobertos.

### Verificação focada

Executar com o PHP local os testes Livewire alterados e os browser tests dos logins em desktop e mobile; em seguida executar `npm run build` para validar os assets e finalizar com `php ./vendor/bin/pest --parallel --tia --configuration=phpunit-ci.xml` como gate acordado.

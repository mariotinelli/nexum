# Rem Soft Projeto Padrão

Projeto Laravel com Livewire para gestão e consulta de funcionalidades da plataforma Rem Soft Projeto Padrão.

## Stack atual

- PHP `8.4`
- Laravel `13`
- Livewire `4`
- Sanctum `4`
- Tailwind CSS `4`
- Alpine.js `3`
- Pest `4` + PHPUnit `12`
- Larastan `3`
- Laravel Boost `2`

## Requisitos de ambiente

- PHP `8.4+`
- Composer `2.8+`
- Node.js `20+` (recomendado LTS)
- NPM `10+`
- Banco de dados MySQL compatível com Laravel 13

## Bibliotecas principais

### Backend

- `laravel/framework` `^13.0`
- `livewire/livewire` `^4.0`
- `laravel/sanctum` `^4.0`
- [`r2luna/brain`](https://packagist.org/packages/r2luna/brain) `^2.0`
- [`maatwebsite/excel`](https://packagist.org/packages/maatwebsite/excel) `^3.0`
- `predis/predis` `^3.0`
- [`owen-it/laravel-auditing`](https://packagist.org/packages/owen-it/laravel-auditing) `^14.0`
- [`spatie/browsershot`](https://packagist.org/packages/spatie/browsershot) `^5.0`

### Frontend

- `tailwindcss` `^4.0`
- [`daisyui`](https://daisyui.com/) `^5.0`
- `alpinejs` `^3.0`
- `@alpinejs/collapse` `^3.0`
- `@alpinejs/mask` `^3.0`
- `vite` `^8.0`
- `laravel-vite-plugin` `^3.0`

### Qualidade e DX

- [`pestphp/pest`](https://pestphp.com/) `^4.0`
- `pestphp/pest-plugin-laravel` `^4.0`
- `pestphp/pest-plugin-livewire` `^4.0`
- `phpunit/phpunit` `^12`
- `laravel/pint` `^1`
- `larastan/larastan` `^3.0`

## Instalação completa do zero

### 1) Clonar o repositório

```bash
git clone <url-do-repositorio>
cd rem-soft-projeto-padrao
```

### 2) Instalar dependências PHP

```bash
composer install
```

### 3) Instalar dependências JS

```bash
npm install
```

### 4) Configurar ambiente

```bash
cp .env.example .env
php artisan key:generate
```

Atualize as variáveis do `.env` (principalmente banco, fila, mail e serviços externos).

### 5) Preparar banco e storage

```bash
php artisan migrate --seed
php artisan storage:link
```

### 6) Ativar hooks do Git (recomendado)

```bash
npx husky install
```

### 7) Configurar OpenCode

- Instale o Laravel Boost (se solicitar as opções de Claude, Codex, Opencode, etc, selecione sempre `opencode`)

```bash
php artisan boost:install --guidelines --skills --mcp
```

- Copie o arquivo `opencode.example.json` para `opencode.json` e ajuste as configurações conforme necessário.
- Copie o arquivo `boost.example.json` para `boost.json` e ajuste as configurações conforme necessário.

#### Instalação

```bash
npm i -g opencode-ai
```

#### Herd MCP - Configuração (`opencode.json`)

```json
"herd": {
    "type": "local",
    "enabled": true,
    "command": [
        "php",
        "C:/Users/seu-usuario/.config/herd/bin/herd-mcp.phar"
    ],
    "environment": {
        "SITE_PATH": "C:\\Users\\seu-usuario\\Herd\\remsoft\\inova.ai"
    }
}
```

- `enabled`: Ativa ou desativa o uso do Herd MCP (true/false). Se você não usa Herd, você deve desativá-lo.
- `command`: O comando a ser executado para o Herd MCP, troque `seu-usuario` pelo seu nome de usuário do computador
   - Verifique se o seu caminho está igual ao do exemplo, caso contrário, ajuste conforme necessário.
- `environment.SITE_PATH`: Variável de ambiente que define o caminho do site, troque `seu-usuario` pelo seu nome de usuário do computador
   - Verifique se o seu caminho está igual ao do exemplo, caso contrário, ajuste conforme necessário.

#### Herd MCP - Configuração (`boost.json`)

- `herd_mcp`: Ativa ou desativa o uso do Herd MCP para o Laravel Boost (true/false). Se você não usa Herd, você deve desativá-lo.

## Como iniciar o projeto

### Fluxo principal (recomendado)

```bash
composer dev
```

Esse comando sobe em paralelo:

- servidor Laravel
- queue listener
- Vite (`npm run dev`)

### Fluxo manual (alternativo)

Em terminais separados:

```bash
php artisan serve
php artisan queue:work --queue=high_priority,medium_priority,low_priority,long_timeout --sleep=1 --timeout=160 --tries=3
npm run dev
```

## Testes e qualidade

### Rodar testes

```bash
php artisan test
```

### Rodar testes em paralelo

```bash
php artisan test --parallel
```

### Formatação

```bash
vendor/bin/pint --format agent
```

### Análise estática

```bash
composer stan
```

## Convenção de branches

Antes de criar branch, use o prefixo alinhado ao tipo da tarefa:

1. Feature

```bash
git checkout -b feature/983123-task-name
```

2. Enhancement

```bash
git checkout -b enhancement/983123-task-name
```

3. Hotfix

```bash
git checkout -b hotfix/983123-task-name
```

4. Bugfix

```bash
git checkout -b bugfix/983123-task-name
```

5. Task

```bash
git checkout -b task/983123-task-name
```

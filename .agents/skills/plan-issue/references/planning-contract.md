# Contrato de `planning.md`

O planejamento fica ao lado de `task.md` e é o único artefato entregue ao Ralph. Ele não contém hashes, aprovações, cópias do Redmine nem estado operacional.

## Estrutura

Use estas seções de segundo nível antes das fases:

- `Identidade e fontes`: filha, requisito pai e caminhos locais usados.
- `Objetivo`: resultado observável da tarefa.
- `Estado atual`: comportamento e implementação encontrados.
- `Escopo`: o que entra e o que fica fora.
- `Arquitetura`: padrões e decisões existentes que orientam a implementação.
- `Estratégia`: ordem geral e abordagem de testes.
- `Baseline`: comando da suíte completa, resultado inicial e falhas conhecidas.
- `Riscos`: regressões, migrações, segurança e pontos de atenção.

Em `Baseline`, coloque exatamente um bloco cercado com o comando executável da suíte:

````markdown
## Baseline

Comando da suíte completa:

```sh
composer test
```

Resultado inicial: verde.
Falhas conhecidas: nenhuma.
````

Depois, escreva uma ou mais fases em ordem crescente:

```markdown
## Fase 1 — Nome da entrega

### Objetivo
...

### Dependências
...

### Mudanças esperadas
...

### Arquivos prováveis
...

### Limites
...

### Estratégia
...

### Aceite
...

### Verificação focada
...
```

Cada fase deve ser implementável em uma sessão nova, deixar uma mudança coerente para commit e incluir critérios que a validação independente consiga comprovar. Os caminhos são hipóteses fundamentadas, não uma obrigação de editar todos os arquivos listados.

## Revisão

Mostre o arquivo completo ao desenvolvedor. Edite diretamente `planning.md` até ele concordar. Não registre aprovação em outra estrutura. Se o plano mudar depois, a próxima execução do Ralph simplesmente lê o conteúdo atual; para reiniciar todas as fases, apague `.flow/ralph-state.json` depois de decidir o destino dos commits e mudanças existentes.

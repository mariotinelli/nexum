# Execução pelo Ralph

Execute:

```sh
bash <plan-issue>/ralph.sh execute <pasta-dev>/planning.md
```

O Ralph lê as fases e o comando da suíte diretamente de `planning.md`. Ele cria automaticamente `.flow/ralph-state.json` ao lado do plano, contendo somente a fase atual, o gate atual, fases concluídas e seus commits. Apague esse arquivo para esquecer o progresso local; isso não desfaz commits nem mudanças do Git.

## Gates de cada fase

1. **Desenvolvimento:** abre uma sessão nova do Codex para implementar somente a fase, sem commit.
2. **Validação:** abre outra sessão nova e somente leitura para revisar requisito, diff, testes, segurança e padrões.
3. **Testes:** o script executa diretamente a suíte completa declarada no baseline.
4. **Commit:** o script executa `git commit --no-verify` e segue para a próxima fase.

Uma reprovação da validação ou dos testes inicia outra sessão de desenvolvimento com o erro encontrado e repete os gates. O padrão é parar depois de três tentativas; altere com `--max-attempts N`. Falhas operacionais interrompem imediatamente e preservam as mudanças.

O executor não acessa Redmine ou YouTrack, não escolhe modelo nem esforço e não usa subagentes. `codex exec` herda a configuração normal do CLI do usuário. `RALPH_AGENT_COMMAND_JSON` pode fornecer outro runner compatível como um array JSON de argumentos.

## Retomada e segurança mínima

Uma tarefa possui somente uma execução simultânea. Uma fase nova exige worktree limpo. Quando uma tentativa da fase já deixou mudanças, executar o mesmo comando novamente retoma essa fase pelo desenvolvimento. Se o processo terminou logo após o commit, um estado no gate de commit com worktree limpo reconhece o `HEAD` atual como commit da fase e continua.

O diretório `.flow` deve estar ignorado pelo Git. Não existem hashes, fingerprints, manifests, aprovação de baseline, prova por trailer ou reconciliação de evidências. O desenvolvedor continua responsável por revisar o histórico e decidir quando apagar o estado ou desfazer trabalho.

## Saída

Por padrão, o terminal mostra apenas mensagens humanas:

```text
Fase 1 iniciada
[DESENVOLVIMENTO] Gate 1 em andamento [08:48]
[DESENVOLVIMENTO] Gate 1 finalizado [08:52]
[VALIDAÇÃO] Gate 2 aprovado [08:55]
[TESTES] Gate 3 aprovado [08:58]
[COMMIT] Gate 4 finalizado [08:58]
Fase 1 finalizada
```

Erros mostram a causa sanitizada e o caminho do diagnóstico. Prompts, stdout, stderr, testes e eventos estruturados permanecem em `.git/ralph-runtime`. Use `--verbose` para exibir os eventos técnicos no terminal.

Os timeouts padrões são 60 minutos para desenvolvimento, 30 para validação e 60 para testes. Ajuste com `--dev-timeout-minutes`, `--validation-timeout-minutes` e `--tests-timeout-minutes`.

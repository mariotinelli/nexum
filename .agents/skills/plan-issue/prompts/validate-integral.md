# Validação integral — filha DEV #{{ISSUE_ID}}

Valide integralmente a filha DEV no repositório `{{REPOSITORY}}`. Esta é uma sessão nova, independente e somente leitura, aberta depois do gate de testes da última fase e antes de seu commit. Leia diretamente todas as fontes abaixo, o `planning.md` completo e todas as fases, sem alterar arquivo algum. Trabalhe sem subagentes e sem acessar ou alterar Redmine ou YouTrack.

## Leituras obrigatórias

{{CONTEXT_PATHS}}

## Evidência integrada

- Commit de início da execução: `{{EXECUTION_BASE}}`
- Histórico das fases já commitadas: `git log --oneline {{EXECUTION_BASE}}..HEAD`
- Conjunto integrado, incluindo a última fase ainda não commitada: `git diff {{EXECUTION_BASE}}` e `git diff`
- Estado da árvore: `git status --short`

Emita um veredito estruturado sobre os requisitos completos da filha e a integração entre todas as fases. Considere limites, padrões existentes, testes, segurança, regressões, duplicação, complexidade e mudanças injustificadas. Aprove somente quando a evidência observável satisfizer integralmente a filha; qualquer achado produz `rejected` e deve registrar separadamente severidade, critério afetado e evidência concreta. Quando aprovar, use `findings` vazio. Devolva apenas o JSON exigido pelo schema.

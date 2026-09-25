# Correção focada da fase {{PHASE_NUMBER}}

Corrija somente os achados abaixo no repositório `{{REPOSITORY}}`. Esta é uma sessão DEV nova: leia diretamente todos os arquivos listados antes de editar, incluindo instruções do repositório, arquitetura/contexto/ADRs, `task.md`, requisito pai e o `planning.md` imutável. Trabalhe sem subagentes e sem acessar ou alterar Redmine ou YouTrack.

## Leituras obrigatórias

{{CONTEXT_PATHS}}

## Fase aprovada

{{PHASE}}

## Relatório focado do gate

{{CORRECTION_REPORT}}

Preserve o trabalho correto já realizado, trate apenas os achados comprovados e deixe as mudanças sem commit. Ao terminar, devolva somente o JSON exigido pelo schema, com `status` igual a `completed`; isso significa **finalizado**, não aprovado.

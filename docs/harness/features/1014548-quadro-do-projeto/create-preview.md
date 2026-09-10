<!-- project-flow:start -->
## Objetivo
Acompanhar visualmente o fluxo de tarefas de um projeto pela interface WEB em português e executar as transições permitidas.

## Escopo
- Apresentar cinco colunas: Pendente, Em andamento, Pausada, Finalizada e Cancelada, com contagens e estados vazios. Tarefas arquivadas ficam fora do quadro.
- Mostrar nos cards título com acesso ao detalhe, responsável, prioridade, prazo e atraso, estimativa e horas realizadas.
- Oferecer Iniciar, Pausar, Finalizar, Cancelar e Arquivar somente quando permitidos pela situação e autorização. Não oferecer edição direta de situação nem arraste que a altere.
- Permitir consulta aos participantes do projeto e aos administradores, mesmo sem participação. Iniciar, Pausar e Finalizar permanecem exclusivos do responsável atual.
- Manter projetos arquivados somente para consulta.
- Empilhar colunas no mobile e identificar situações com rótulos que não dependam apenas de cor.

## Dependência e limites
Depende de Gestão de Tempo (#1014493), incluindo a integração com as regras de Gestão de Tarefa. O quadro utiliza as transições e os totais existentes, sem redefinir permissões ou regras do cronômetro.

## Coleta
Requisito em coleta. Os detalhes funcionais e critérios de aceite serão definidos na entrevista deste item.
<!-- project-flow:end -->
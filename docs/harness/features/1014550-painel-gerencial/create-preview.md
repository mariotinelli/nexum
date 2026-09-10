<!-- project-flow:start -->
## Objetivo
Acompanhar progresso, atrasos e esforço pela interface WEB em português, conforme o papel do usuário em cada projeto.

## Escopo
- Membros consultam suas próprias tarefas e horas; gestores consultam a equipe dos projetos gerenciados; administradores consultam equipes e indicadores de todos os projetos.
- Apresentar projetos ativos, distribuição de tarefas pelas situações vigentes, tarefas atrasadas e finalizadas no período, com filtro de finalizações.
- Comparar horas estimadas e realizadas e apresentar horas por membro.
- Calcular progresso por Finalizadas / (Pendentes + Em andamento + Pausadas + Finalizadas), com 0% no conjunto vazio. Canceladas e arquivadas não compõem progresso nem atraso.
- Abrir projetos, tarefas filtradas e Minhas Tarefas pelos links e indicadores correspondentes.
- Apresentar gráficos rotulados, estados de vazio, carregamento, erro e sucesso e conteúdo empilhado no mobile, respeitando o recorte autorizado.

## Dependências e limites
Depende de Consulta de Tarefas (#1014465) e Minhas Tarefas (#1014547). Agrega dados existentes de projetos, tarefas e apontamentos, sem duplicar sua criação nem redefinir permissões e regras de tempo.

## Coleta
Requisito em coleta. Os detalhes funcionais e critérios de aceite serão definidos na entrevista deste item.
<!-- project-flow:end -->
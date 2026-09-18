# Disciplina de aplicação de revisões

Use esta disciplina somente para a revisão semântica funcional corrente, especificamente aprovada e vinculada ao hash do impacto localizado. Uma nova revisão, rejeição, mudança de baseline ou ampliação do impacto encerra a autoridade anterior.

## Escolher a representação

Classifique cada tarefa remota pelo status nativo observado no instante do plano: não iniciada, em andamento, concluída ou cancelada. Trabalho novo vira nova filha com os contratos vigentes de título, descrição, cobertura, QA, adoção e dependências. Tarefa em andamento pode receber somente a alteração localizada, depois de prévia concreta e aprovação adicional do tech lead ligada à tarefa, ao snapshot corrente e à mutação. Tarefa concluída permanece fora do delta; correção ou acréscimo vira nova filha ligada à revisão. União ou substituição cancela somente tarefa comprovadamente não iniciada e registra motivo e substitutos no journal da transição nativa.

**Concluído quando:** cada impacto aprovado possui uma representação, toda tarefa concluída está fora das mutações e cada cancelamento tem prova de não início, motivo e substitutos.

## Reconciliar antes de agir

Compare novamente payload e status da tarefa imediatamente antes de cada mutação. Mudança desde a prévia invalida a intenção ou sua aprovação: localize o novo estado, refaça o delta e apresente nova prévia. Use o ID e o nome exatos do catálogo nativo para classificar e transicionar status; ausência, ambiguidade ou divergência interrompe a aplicação.

Modele criação, atualização, cancelamento, adição e remoção de relação com intenção persistida antes da chamada, resultado depois dela e observação por readback para qualquer resultado incerto. Uma operação reconciliada não volta à ferramenta remota.

**Concluído quando:** cada operação começou com snapshot corrente comprovado e toda tentativa incerta foi observada como presente ou ausente antes de repetir.

## Provar preservação

No readback final, confira payloads e status esperados, razão e substitutos dos cancelamentos, bloqueios DEV→QA afetados, ausência somente das arestas aprovadas para remoção e presença exata de relações não afetadas. Confira também filhas concluídas, não afetadas, adotadas e externas, evidências de Study, divergência e revisão semântica, além do status de execução do pai.

**Concluído quando:** o delta inteiro está comprovado, todo item fora dele permanece idêntico e o pai conserva o status observado antes da aplicação.

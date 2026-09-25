# Reconciliação local de publicações históricas

Use este ramo somente quando uma publicação DEV/QA v1 ou um Study v1 já concluiu sua criação ou adoção, mas ainda conserva a representação posicional histórica em vez de `tasks/<tipo>-<id>-<slug>/task.md`. Ele materializa uma projeção local; todas as chamadas Redmine ficam fora deste ramo, e o estado, descrições, hashes, aprovações, tentativas e baselines históricos permanecem byte a byte.

## Releitura e prévia exata

Leia novamente o pai e cada filha gerenciada, incluindo todos os campos e relações, pelos tools Redmine de leitura. Grave somente a resposta sanitizada em `.work/slices-reconciliation-readback.json`. Para DEV/QA use `{"parent": {...}, "children": [...]}` com cada filha gerenciada exatamente uma vez; para Study use `{"parent": {...}, "study": {...}}`.

Execute:

```sh
python <project-slices>/scripts/manage_reconciliation.py prepare .flow/slices-reconciliation.json \
  --legacy .flow/<estado-historico>.json \
  --readback .work/slices-reconciliation-readback.json \
  --preview slices/reconciliation.md
```

O helper aceita somente estado v1 com resultado remoto concluído e ID inequívoco. Ele valida pai, projeto, tipo, tracker, status, prioridade, heranças, responsável e datas vazios, estimativa, título, descrição e relações relevantes. Divergência, publicação parcial, IDs ausentes ou repetidos, evidência alterada, caminho inseguro ou colisão interrompem sem gravar tarefas.

`slices/reconciliation.md` mostra cada destino, SHA-256 e os bytes Markdown exatos. Mostre-o integralmente ao tech lead. A conclusão desta fase exige que a prévia exista, os hashes do estado histórico e do readback permaneçam atuais e nenhuma pasta canônica tenha sido criada.

## Decisão corrente e materialização

Depois de o tech lead aprovar explicitamente a prévia corrente, execute:

```sh
python <project-slices>/scripts/manage_reconciliation.py approve .flow/slices-reconciliation.json \
  --actor "<tech lead>" --at "<ISO-8601>"
python <project-slices>/scripts/manage_reconciliation.py materialize .flow/slices-reconciliation.json \
  --at "<ISO-8601>"
```

A decisão referencia o hash que combina origem, readback, destinos e conteúdo exato. Antes de aprovar e antes de materializar, o helper relê toda a evidência e repete a validação. Qualquer mudança exige preservar o registro existente, resolver a divergência e preparar outra reconciliação deliberada; aprovação anterior nunca migra para outra prévia.

A gravação atômica produz o mesmo contrato `task.md` da publicação corrente. Uma pasta preexistente do mesmo tipo e ID preserva seu slug quando o conteúdo coincide; múltiplas pastas ou conteúdo diferente são conflito. Uma execução concluída pode ser repetida sem alterar arquivos.

**Concluído quando:** `.flow/slices-reconciliation.json` está `completed`, cada `task.md` coincide com os bytes aprovados, os arquivos históricos conservam seus hashes originais e nenhuma mutação remota foi solicitada.

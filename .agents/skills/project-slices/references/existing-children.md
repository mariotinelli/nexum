# Filhas existentes e caminho somente QA

## Descobrir e decidir

Leia o pai com `children`, percorra todas as páginas das filhas abertas e fechadas e obtenha cada issue integralmente com relações pelo MCP. Grave em `.work` somente o snapshot sanitizado com projeto, pai, paginação, IDs, tracker e campos, título, descrição, estimativa e relações. Apresente todas ao tech lead; a existência de filhas não prova que o item pai foi fatiado.

Para cada filha, registre no `existing_children_review` do plano uma decisão `adopt` ligada a uma key proposta ou `keep-external`. Uma adoção nomeia toda divergência aceita entre a entrega proposta e o baseline remoto; projeto ou pai divergentes impedem a adoção. Uma decisão externa não seleciona key nem autoriza alteração. O snapshot completo, seu hash, o ator, o instante e o motivo entram na revisão de publicação aprovada.

Antes de pedir a decisão, apresente cada filha como `#<ID> — <título completo exatamente como no Redmine>`, preservando todos os prefixos e o sufixo. Mostre a ação proposta (adotar ou manter externa), tracker, status, estimativa, relações e divergências. Para adoção, identifique também o título completo do slice de destino quando diferir do título remoto; a key é apenas um detalhe secundário. Nos bloqueios, identifique cada tarefa relacionada pelo título completo e ID confirmado quando existir. A pergunta de aprovação deve remeter a essa lista identificada, sem substituir títulos por `dev-1`, `qa`, somente sufixos ou resumos como “QA da Autenticação”.

Exemplo: `#1014746 — [DEV] [WEB] [PUBLICO] Autenticação - Entrada e navegação de contas ativas`; ação proposta: adotar como a entrega de mesmo título (chave interna `dev-1`). Exibir o título na revisão é necessário para identificar a tarefa; ele continua fora do corpo da descrição publicada.

**Concluído quando:** cada filha foi apresentada com ID, título completo e ação proposta, cada ID descoberto possui exatamente uma decisão do tech lead, toda adoção referencia uma key única e toda divergência está visível ou bloqueia a prévia.

## Retomar sem duplicar

Trate uma adotada como origem remota observada, não como criação concluída. Preserve seu ID na revisão e use-o nas relações aprovadas. Em retomada, valide os hashes e releia antes de repetir qualquer operação ambígua; `begin-create` é exclusivo das keys novas. Filhas externas ficam fora de `children` e `operations` gerenciados e aparecem no readback apenas para provar preservação.

**Concluído quando:** cada key adotada conserva o mesmo ID, somente keys novas possuem operação de criação e o readback mantém filhas e relações externas.

## Encaminhar somente QA

Use este ramo apenas quando a inspeção de código cobre integralmente cada requisito. Materialize uma proposta sem slices, classifique cada linha de cobertura como `existing`, cite evidência atual e mostre ao tech lead que nenhuma DEV é necessária. A aprovação da decomposição liga essa confirmação ao hash e à revisão; mudança posterior invalida a autoridade de publicação.

Prepare exatamente uma filha com título `[QA] ` seguido do título integral do item pai. Neste ramo, e somente nele, `blocked_by` é vazio e não existem relações DEV fictícias. A QA verifica a Feature ou Bug completo e não aprova a decisão.

**Concluído quando:** a proposta aprovada possui slices vazio, cobertura `existing` exaustiva e evidências atuais; a publicação aprovada e conferida contém somente a QA.

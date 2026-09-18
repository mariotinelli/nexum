# Fatiamento sequencial de escopo

Use este ramo quando o tech lead pedir um escopo ou não indicar uma Feature. Ele coordena várias execuções do fluxo principal; cada Feature conserva sua própria inspeção, duas aprovações, publicação e releitura.

## Selecionar

Sem entrada, execute `manage_scope.py list <docs/harness>` e apresente somente escopos que tenham ao menos uma Feature ativa, aprovada e ainda pendente ou em andamento. Mostre também `fatiadas/total` e as quantidades `pendente`, `em andamento`, `concluída` e `aguardando requisitos`, então pergunte qual escopo processar. O total inclui toda Feature ativa do catálogo; Bugs e itens retirados não entram.

O helper valida o estado real do `project-flow`, a aprovação da projeção completa do catálogo e sua ordem. Uma Feature sem artefato ou requisito concluído fica `aguardando requisitos`; ela não desaparece do total e não impede trabalhar outra Feature elegível. Caminho inseguro, vínculo de catálogo obsoleto, tipo, entrega ou ID Redmine divergente é erro, não espera.

**Concluído quando:** o tech lead escolheu uma das opções derivadas do catálogo aprovado e viu a distribuição integral das Features ativas.

## Iniciar ou retomar

Para uma seleção nova, execute:

```sh
python <project-slices>/scripts/manage_scope.py start <scope-dir> --actor "<tech lead>" --at "<ISO-8601>"
```

O estado fica em `<scope-dir>/.flow/slices-scope-state.json`, separado do progresso de requisitos e execução do `project-flow`. Ele se vincula ao `internal_identity`, projeto e hash da projeção aprovada do catálogo, não aos bytes mutáveis de `scope-state.json`.

Se o estado estiver pausado, execute `resume`. Se estiver ativo, execute `refresh`. Retome `current_item_id`; jamais escolha por um flag informado em conversa. A conclusão prévia só vale quando `slices-publication.json` passa pelo validador RST13, possui a aprovação final corrente, todas as criações e relações concluídas e evidência de readback. Assim, uma retomada pula a Feature já publicada sem repetir seus gates ou operações.

**Concluído quando:** o estado durável aponta para a primeira Feature elegível ainda não processada na ordem aprovada, ou explicita que só restam requisitos em espera.

## Processar uma Feature

Execute integralmente o ramo de Feature deste skill para `current_item_id`. Dependências do catálogo explicam a ordem, mas não bloqueiam o fatiamento. Um bloqueio de implementação pertence às filhas e também não interrompe o processamento das próximas Features.

Cada Feature mantém separadamente:

1. conferência do requisito aprovado e publicado;
2. aprovação da decomposição pelo tech lead;
3. aprovação da prévia final de publicação pelo tech lead;
4. criação e relações reconciliadas;
5. readback integral das filhas e bloqueios.

Não agregue aprovações ou publicações entre Features.

**Concluído quando:** a publicação individual está `completed` com seu readback validado, ou a Feature permanece explicitamente pendente/em andamento sem alegação de conclusão.

## Mostrar progresso e decidir

Depois da conclusão individual, rode `refresh`, mostre a distribuição atual e pergunte ao tech lead se deseja continuar ou parar. Registre exatamente a resposta:

```sh
python <project-slices>/scripts/manage_scope.py decide <scope-dir> --after-item <catalog-item-id> --decision continue --actor "<tech lead>" --at "<ISO-8601>"
python <project-slices>/scripts/manage_scope.py decide <scope-dir> --after-item <catalog-item-id> --decision stop --actor "<tech lead>" --at "<ISO-8601>"
```

`stop` pausa sem perder a próxima Feature; `resume` registra a retomada e recalcula a próxima elegível sem duplicar a concluída. A decisão fica ligada ao hash da observação de progresso apresentada.

**Concluído quando:** a decisão posterior à Feature está persistida e o próximo passo exibido coincide com o estado validado.

## Concluir

O helper conclui automaticamente apenas quando `fatiadas == total`. Uma Feature ativa aguardando requisitos mantém o escopo incompleto, mesmo que não exista outra elegível agora. Reporte essa espera sem transformar requisitos ausentes em item retirado. Mostre também `dependency_status`: ele acompanha se relações externas estão `pending`, `refining` ou `ready` sem desfazer a publicação concluída nem afirmar que a capacidade bloqueadora já foi implementada.

**Concluído quando:** todas as Features ativas possuem roteamento DEV/QA individual completo e verificado; caso contrário, o estado preserva exatamente o progresso e a razão observável da espera.

# Descrições para quem executa

## Escrever a entrega

Use `delivery` para explicar o contexto funcional relevante e a mudança esperada. Quando a inspeção comprovar comportamento existente, diferencie o que será adaptado do que será preservado. Para uma capacidade nova, explique o resultado a criar sem inventar um cenário anterior. Mantenha arquivos, símbolos e conclusões técnicas detalhadas na evidência de inspeção.

Em `limits`, registre somente fronteiras que evitem dúvidas reais sobre a responsabilidade da tarefa. Evite repetir a entrega ou enumerar todas as Features excluídas. Use linguagem do produto: “manter o acesso por 30 dias” e “sair somente deste navegador” são mais diretos que “comportamento temporal da lembrança” e “isolamento da saída”.

**Concluído quando:** o executor identifica o que mudar e o que preservar sem consultar a conversa, sem receber uma receita técnica.

## Escrever critérios e relações

Escreva uma condição verificável por item, separando cenários com resultados independentes. Condições relacionadas podem ficar juntas quando isso facilitar a leitura. Preserve todos os detalhes aprovados de prazo, dispositivo, permissão e acessibilidade; não imponha limite de tamanho ou quantidade que elimine cobertura. Use uma única seção de critérios de aceite. `kind` permanece no contrato interno; o texto do critério não deve repetir os rótulos Sucesso, Erro ou Permissão.

Em `dependencies`, nomeie a capacidade necessária e a tarefa responsável. Distinga impedimento para iniciar de integração necessária para concluir, sem transformar esta última automaticamente em `blocked_by`. Quando não houver relações relevantes, basta informar que não há dependências. Justificativas sobre como o fluxo calcula bloqueios pertencem ao planejamento, não à descrição.

Referencie outras tarefas pelo nome, e pelo link quando o destino já existir e estiver confirmado. Números como “entrega 1” só identificam itens dentro da prévia; não bastam na descrição independente. Não invente IDs nem acrescente links ao conteúdo aprovado durante a publicação sem a revisão correspondente.

Mantenha a rastreabilidade em referências compactas ao requisito pai e aos IDs cobertos. Referências complementam os critérios; não substituem sua explicação.

**Concluído quando:** cada condição atribuída está representada, os critérios podem ser verificados individualmente e as relações são compreensíveis fora da prévia.

## Exemplo editorial: Autenticação

Os trechos abaixo ilustram escrita, não uma nova decomposição nem uma descrição completa. Use fatos da inspeção corrente e preserve todos os demais requisitos ao aplicar o exemplo.

Antes: “Permitir que pessoas de todos os perfis com conta ativa entrem no Nexum.”

Depois, quando a inspeção comprovar a restrição atual: “O login atual restringe a entrada de alguns perfis. Ajustar a entrada para que qualquer conta ativa acesse o painel permitido ao seu perfil, preservando as restrições administrativas.”

Antes: “Erro: Campos obrigatórios ausentes ou e-mail inválido exibem validação; credenciais inválidas recusam a entrada; conta inativa recebe orientação.”

Depois:

- Sem e-mail ou senha, o formulário informa os campos obrigatórios e permite corrigir sem autenticar.
- Com e-mail em formato inválido, o formulário informa a validação e permite corrigir sem autenticar.
- Com credenciais incorretas, a entrada é recusada com mensagem acessível.
- Com conta inativa, a entrada é recusada e a mensagem orienta solicitar reativação.

Antes: “Usa o bloqueio da entrega 1; compartilhar código não constitui bloqueio de início.”

Depois: “Pode iniciar com a base de login existente. Para concluir, integrar com ‘Autenticação - Entrada e navegação de contas ativas’ e verificar que a lembrança de acesso também recusa contas desativadas.”

## Revisar antes da aprovação

Leia a descrição isoladamente, como a pessoa que receberá a tarefa. Confira a mudança esperada, a preservação do comportamento existente, a cobertura de cada requisito, a separação dos cenários e a identificação das tarefas relacionadas. Retire repetições, estimativas já mantidas em campo próprio e comentários administrativos sobre aprovação ou funcionamento do fluxo.

**Concluído quando:** a descrição é autossuficiente e legível, sem omissões de cobertura, ampliação de escopo ou linguagem administrativa desnecessária. Essa revisão é semântica; um helper estrutural não comprova qualidade de escrita.

# Evidência da inspeção

## Conferir afirmações técnicas

Para cada afirmação que sustenta um corte ou sua dispensa, registre o comportamento observado e a origem verificável: arquivo e símbolo ou linha, configuração efetiva, teste ou resultado de execução. Confira valores padrão no código da versão instalada e verifique sobrescritas no projeto. Registre valor, unidade e condição de aplicação; diferencie duração de cookie, validade de sessão e renovação quando essas distinções afetarem o requisito.

Separe o que foi constatado por leitura do que foi executado. Um teste encontrado só comprova o cenário que ele exercita; informe se foi executado. Se a configuração efetiva ou algum caminho relevante não puder ser confirmado, registre a incerteza e seu impacto sem ler ou persistir credenciais. Resolva fatos técnicos pela inspeção; decisões de produto permanecem com o tech lead.

**Concluído quando:** toda afirmação usada na classificação possui origem conferida, e valores ou condições desconhecidos estão explícitos, sem serem apresentados como comportamento confirmado.

## Classificar o comportamento completo

Confronte a evidência com todas as condições do requisito: atores, permissões, caminhos de acesso, transições, prazos e dispositivos, quando aplicáveis. A presença de um mecanismo isolado, como exclusão lógica, logout ou filtro de menu, exige seguir os caminhos que o utilizam antes de concluir sobre o comportamento completo.

Use `existing` somente quando a evidência sustentar integralmente o resultado aprovado. A leitura do caminho completo pode bastar; execute uma verificação direcionada quando a conclusão depender de comportamento em execução ainda incerto. Para implementação parcial, registre o que já funciona e o que falta, classifique a inspeção como `adapt` e atribua o requisito ao slice que entrega a diferença. Ausência de teste, por si só, não significa ausência de implementação. Evidência inconclusiva permanece como incerteza; se impedir os cortes completos, encaminhe ao ramo de Study do fluxo chamador.

**Concluído quando:** cada classificação `existing` sustenta todas as condições relevantes, cada adaptação identifica a diferença a entregar e nenhuma incerteza foi convertida em cobertura confirmada.

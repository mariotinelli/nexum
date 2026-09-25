## Entrega

Manter a lembrança de acesso por 30 dias a partir do login e permitir sair apenas do navegador atual.

## Escopo e limites

Inclui prazo fixo da lembrança, retorno após fechar o navegador e saída com remoção de sessão e lembrança locais. Não redefine a validade da sessão ordinária nem implementa recuperação de senha ou administração de contas. Usa o bloqueio de contas desativadas da entrega 1; a experiência acessível dos controles é coberta por ela.

## Critérios de aceite

- Com conta ativa e Lembrar-me marcado, fechar e reabrir o navegador dentro dos 30 dias do login permite restaurar o acesso.
- Encerrados os 30 dias, a lembrança não autentica. Sem sessão válida, o usuário precisa entrar novamente; acessos intermediários não renovam automaticamente o prazo contado desde o login.
- Com acesso válido em dois navegadores, Sair encerra a sessão e remove a lembrança somente no navegador usado. Retornar nele exige login quando não houver nova sessão válida.
- A saída em um navegador preserva o acesso e a lembrança ainda válidos no outro, inclusive ao fechá-lo e reabri-lo dentro do prazo.
- A lembrança não permite contornar desativação: conta inativa não recupera acesso; a próxima ação de cada sessão da conta desativada é bloqueada, preservando a garantia da entrega 1.

## Dependências

Nenhum bloqueio para iniciar: o login, a lembrança e a saída já têm base implementada. Coordenar a integração com a entrega 1 para verificar o comportamento completo de contas desativadas; compartilhar código não constitui bloqueio de início.

## Referências

Item pai Redmine #1014446; regras/critérios R4, R5, CA5, CA6, CA7.

<!-- project-slices-child:9144f6ecd5120782d3dd7ce49efc8da616d725e18f47b1d227161eea60b2e61b -->

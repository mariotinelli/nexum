<!-- project-flow:start -->
## Objetivo e resultado esperado
Permitir que usuários autenticados mantenham seus próprios dados pessoais e alterem a própria senha pela interface WEB responsiva em português. Dados pessoais e troca de senha ficam em cards separados, cada um com seu componente e botão, com validação e salvamento independentes.

## Atores e permissões
Todos os usuários autenticados, incluindo administradores nas funções pessoais. Somente os próprios dados podem ser consultados e alterados. Meu Perfil não administra outras contas nem altera permissões ou participação em projetos.

## Fluxos principais
**Card Dados Pessoais:** apresenta Nome e E-mail atuais e o botão **Salvar dados**, em componente próprio. Ao salvar valores válidos, atualiza somente os dados pessoais e apresenta confirmação. O novo e-mail passa a valer imediatamente para login e recuperação, sem confirmação por e-mail.

**Card Troca de Senha:** apresenta Senha atual, Nova senha, Confirmar nova senha e o botão **Alterar senha**, em outro componente. Sua validação e seu salvamento são independentes do card Dados Pessoais. Com senha atual correta e nova senha válida e confirmada, atualiza a senha e apresenta sucesso. Mantém a sessão atual, encerra as demais e remove Lembrar-me de todos os dispositivos.

## Regras e exceções
- Nome e e-mail obrigatórios; e-mail válido e não utilizado por outra conta. O próprio e-mail atual é permitido.
- Cada botão valida e salva apenas seu card. Dados válidos podem ser salvos mesmo com campos de senha vazios ou inválidos; trocar senha não salva dados pessoais pendentes.
- Trocar senha exige senha atual correta e os três campos preenchidos e válidos.
- Nova senha com mínimo de 8 caracteres, maiúscula, minúscula, número e símbolo. Rejeitar senhas conhecidas em vazamentos; confirmação idêntica obrigatória.
- Erros impedem a ação correspondente e permitem correção, sem executar a outra ação.
- A troca mantém a sessão atual, encerra as demais e remove todas as lembranças de acesso.

## Critérios de aceite
1. Ao abrir Meu Perfil autenticado, apresentar os próprios dados e os dois cards com componentes e botões independentes.
2. Ao salvar nome e e-mail válidos, atualizar somente esses dados e apresentar sucesso, sem exigir ou alterar senha.
3. Nome ou e-mail ausentes, e-mail inválido ou pertencente a outra conta impedem salvar dados e apresentam validação; manter o próprio e-mail é permitido.
4. Após salvar novo e-mail, login e recuperação identificam essa conta pelo novo endereço; o anterior deixa de identificá-la nesses fluxos.
5. Campos de senha vazios ou inválidos não impedem salvar dados pessoais válidos.
6. Trocar senha com valores válidos não salva alterações pendentes de nome ou e-mail.
7. Senha atual ausente ou incorreta, nova senha fora da política ou confirmação ausente ou diferente impedem a troca, com validação no card correspondente.
8. Após troca bem-sucedida, a senha anterior não autentica e a nova passa a autenticar.
9. Após trocar a senha pelo perfil, a sessão atual permanece, as demais deixam de permitir continuidade e todas as lembranças de acesso são removidas.
10. Tentativas de acessar ou alterar dados de outra conta são recusadas. Salvar o próprio perfil não modifica permissões ou participação em projetos.
11. Em desktop e mobile, ambos os cards são utilizáveis por teclado, com labels, foco visível e mensagens acessíveis de carregamento, validação, erro e sucesso da ação executada.

## Dependências e limites
Depende de Autenticação (#1014446). Relação 659 existente: #1014446 bloqueia #1014448. Usa a navegação autenticada existente.

Inclui consulta e edição dos próprios dados, troca da própria senha, efeitos confirmados sobre login, recuperação, sessões e lembranças, com ações independentes. Interface responsiva em português com contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento. Senhas protegidas e erros sem exposição de dados sensíveis.

Administração de outras contas, permissões, ativação e desativação de usuários, recuperação de senha sem sessão e gestão de projetos pertencem às respectivas Features. Sem confirmação do novo e-mail, aplicativo nativo ou API pública nesta entrega.

## Requisito canônico e evidências
Documento aprovado: docs/harness/features/1014448-meu-perfil/feature.md
Evidências: design-profile e design-guide. Decisões Q11–Q14 e confirmação em interview.md. Dois cards, componentes e botões independentes substituem a ação única do design por decisão de Mário Tinelli. Política de senha alinhada à Recuperação de Senha. Requisito aprovado por Mário Tinelli.
<!-- project-flow:end -->
<!-- project-flow:start -->
## Objetivo

Permitir que usuários autenticados mantenham seus próprios dados pessoais e alterem a própria senha, com ações independentes, pela interface WEB responsiva em português.

## Resultado esperado

O usuário atualiza nome e e-mail ou troca a senha sem administrar outras contas. Cada ação valida e salva apenas seu card.

## Atores e permissões

Usuários autenticados de todos os perfis, incluindo administradores nas funções pessoais. Acesso restrito aos próprios dados, sem alterar permissões, perfil administrativo ou participação em projetos.

## Histórias de usuário

1. Como usuário autenticado, quero consultar e atualizar meu nome e e-mail para manter meus dados corretos.
2. Como usuário, quero que meu novo e-mail passe a valer imediatamente para login e recuperação.
3. Como usuário, quero trocar minha senha confirmando a senha atual para manter meu acesso sob controle.
4. Como usuário, quero salvar dados e senha independentemente para que uma ação não dependa do preenchimento da outra.
5. Como usuário, quero continuar na sessão atual após trocar a senha, encerrando os demais acessos e lembranças anteriores.

## Fluxo principal

A página apresenta dois cards, cada um com seu componente e botão próprios, conforme decisão explícita do usuário.

**Dados Pessoais:** apresenta Nome e E-mail atuais e o botão **Salvar dados**, em componente próprio. Ao salvar valores válidos, atualiza somente os dados pessoais e apresenta confirmação. O novo e-mail passa a valer imediatamente para login e recuperação, sem confirmação por e-mail.

**Troca de Senha:** apresenta Senha atual, Nova senha, Confirmar nova senha e o botão **Alterar senha**, em outro componente. Sua validação e seu salvamento são independentes do card Dados Pessoais. Com senha atual correta e nova senha válida e confirmada, atualiza a senha e apresenta sucesso. Mantém a sessão atual, encerra as demais e remove Lembrar-me de todos os dispositivos.

## Fluxos alternativos e exceções

- Nome ou e-mail ausentes, e-mail inválido ou utilizado por outra conta: impedir o salvamento dos dados e apresentar validação.
- Senha atual ausente ou incorreta: impedir a troca e apresentar validação.
- Nova senha fora da política ou confirmação ausente ou diferente: impedir a troca e permitir correção.
- Campos de senha vazios ou inválidos não impedem salvar dados válidos no outro card.
- Trocar a senha não salva alterações pendentes de nome ou e-mail.
- Erros de uma ação ficam associados ao card correspondente, sem executar a outra ação.

## Regras de negócio

R1. O usuário consulta e altera somente seus próprios dados.
R2. Nome e e-mail são obrigatórios; o e-mail deve ser válido e não utilizado por outra conta. Manter o próprio e-mail é permitido.
R3. Novo e-mail salvo vale imediatamente para login e recuperação, sem etapa de confirmação por e-mail.
R4. Dados pessoais e troca de senha possuem cards, componentes e botões separados. Cada ação valida e salva apenas seu card.
R5. Trocar a senha exige senha atual correta e todos os campos dessa ação preenchidos e válidos.
R6. A nova senha exige ao menos 8 caracteres, maiúscula, minúscula, número e símbolo. Senhas conhecidas em vazamentos são rejeitadas; a confirmação deve ser idêntica.
R7. Após a troca, manter a sessão atual, encerrar as demais e remover Lembrar-me de todos os dispositivos.
R8. Meu Perfil não altera permissões nem administra outras contas.

## Dados percebidos pelo usuário

Card Dados pessoais: Nome, E-mail e botão Salvar dados. Card Troca de senha: Senha atual, Nova senha, Confirmar nova senha e botão Alterar senha. Cada card apresenta mensagens de carregamento, validação, erro e sucesso da sua ação.

## Critérios de aceite

CA1 — Com usuário autenticado, ao abrir Meu Perfil, apresentar seus dados atuais e os dois cards com botões independentes. [R1, R4]
CA2 — Com nome e e-mail válidos, ao salvar dados, atualizar somente esses campos e apresentar sucesso, sem exigir ou alterar a senha. [R2, R4]
CA3 — Com nome ou e-mail ausentes, e-mail inválido ou pertencente a outra conta, ao salvar dados, recusar a alteração e informar a validação. O próprio e-mail atual permanece aceito. [R2]
CA4 — Após salvar um novo e-mail, ao entrar novamente ou solicitar recuperação, usar o novo endereço; o anterior deixa de identificar essa conta nesses fluxos. [R3]
CA5 — Com campos de senha vazios ou inválidos, ao salvar dados pessoais válidos, concluir somente o salvamento dos dados. [R4]
CA6 — Com alterações pendentes no card de dados, ao trocar a senha com valores válidos, atualizar somente a senha, sem salvar nome ou e-mail pendentes. [R4]
CA7 — Com senha atual incorreta ou ausente, nova senha fora de qualquer regra ou confirmação ausente ou diferente, ao trocar a senha, recusar a alteração e apresentar validação no card correspondente. [R5–R6]
CA8 — Com senha atual correta e nova senha válida e confirmada, ao trocar, apresentar sucesso; a senha anterior deixa de autenticar e a nova passa a autenticar. [R5–R6]
CA9 — Com sessões em vários dispositivos, ao trocar a senha pelo perfil, manter a sessão atual, impedir continuidade das demais e remover todas as lembranças de acesso. [R7]
CA10 — Ao tentar consultar ou alterar dados de outra conta por Meu Perfil, recusar o acesso; salvar o próprio perfil não altera permissões ou participação em projetos. [R1, R8]
CA11 — Em desktop e mobile, ao usar os dois cards, manter campos e botões utilizáveis por teclado, com labels, foco visível e mensagens acessíveis da ação executada. [Fluxos; guia de design]

## Dependências

Autenticação, issue #1014446. Relação nativa 659 já registrada: Autenticação bloqueia Meu Perfil. A interface utiliza a navegação autenticada existente.

## Dentro do escopo

Consulta e edição dos próprios dados, alteração da própria senha, efeitos confirmados sobre login, recuperação, sessões e lembranças, e ações independentes. Interface responsiva em português com os requisitos explícitos do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento. Senhas protegidas e erros sem exposição de dados sensíveis.

## Fora do escopo

Administração de outras contas, permissões, ativação e desativação de usuários, recuperação de senha sem sessão e gestão de projetos pertencem às respectivas Features. Sem confirmação do novo e-mail, aplicativo nativo ou API pública nesta entrega.

## Requisito canônico

Documento aprovado por Mário Tinelli: docs/harness/features/1014448-meu-perfil/feature.md
<!-- project-flow:end -->
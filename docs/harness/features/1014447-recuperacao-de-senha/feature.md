# [WEB] [PUBLICO] Recuperação de Senha

Issue: #1014447. Versão proposta para aprovação.

## Objetivo

Permitir que uma pessoa que esqueceu sua senha recupere o acesso à própria conta ativa, por uma interface WEB responsiva em português, sem revelar a existência do e-mail informado.

## Resultado esperado

A pessoa recebe instruções por e-mail, define e confirma uma nova senha mediante link válido e retorna ao login. Sessões e lembranças anteriores deixam de permitir acesso.

## Atores e permissões

Pessoas sem sessão podem solicitar recuperação. Somente contas ativas recebem instruções e podem redefinir a senha. Recuperar a senha não reativa contas nem concede novas permissões.

## Histórias de usuário

1. Como pessoa que esqueceu a senha, quero solicitar instruções por e-mail para recuperar meu acesso.
2. Como destinatário, quero definir e confirmar uma nova senha por um link válido para voltar a entrar.
3. Como pessoa com link inválido ou expirado, quero identificar o impedimento e solicitar novas instruções.
4. Como titular da conta, quero que a redefinição encerre os acessos anteriores em todos os dispositivos.

## Fluxo principal

1. Acessar a recuperação a partir do login.
2. Informar o e-mail e acionar Enviar instruções.
3. Receber confirmação genérica; para conta ativa, receber o e-mail com o link.
4. Abrir o link válido e informar Nova senha e Confirmar nova senha.
5. Acionar Salvar nova senha.
6. Com as validações atendidas, salvar a nova senha, encerrar todas as sessões e remover todas as lembranças de acesso.
7. Informar o sucesso e retornar ao login para entrar com a nova senha.

## Fluxos alternativos e exceções

- E-mail ausente ou inválido: apresentar validação e permitir correção.
- E-mail não cadastrado ou conta inativa: apresentar a mesma confirmação, sem enviar instruções.
- Conta desativada após receber o link: impedir a redefinição enquanto estiver inativa.
- Link inválido, expirado, substituído ou utilizado: impedir a redefinição e informar o impedimento.
- Nova senha fora das regras ou confirmação diferente: informar a validação e permitir correção.
- Nova solicitação antes de 60 segundos: aplicar a mesma espera e retorno, independentemente da existência da conta.
- Voltar ao login permanece disponível na jornada de recuperação.

## Regras de negócio

R1. A solicitação exige e-mail válido e não revela se ele está cadastrado.
R2. Somente contas ativas recebem instruções e podem redefinir a senha; a recuperação não altera seu estado.
R3. O link vale por 60 minutos a partir da emissão e permite uma única redefinição bem-sucedida. Novo envio invalida o anterior.
R4. Deve haver 60 segundos entre solicitações para o mesmo e-mail, com comportamento igual para contas existentes e inexistentes.
R5. A nova senha exige ao menos 8 caracteres, maiúscula, minúscula, número e símbolo. Senhas conhecidas em vazamentos são rejeitadas. A confirmação deve ser idêntica.
R6. Redefinir a senha encerra todas as sessões e remove Lembrar-me em todos os dispositivos.
R7. Após sucesso, retornar ao login, sem autenticação automática.

## Dados percebidos pelo usuário

E-mail, Nova senha, Confirmar nova senha, ações Enviar instruções, Salvar nova senha e Voltar ao login; instruções recebidas por e-mail e mensagens de carregamento, validação, erro e sucesso.

## Critérios de aceite

CA1 — Com e-mail de conta ativa, ao solicitar instruções, apresentar confirmação genérica e enviar o link de recuperação. [R1–R2]
CA2 — Com e-mail inexistente ou conta inativa, ao solicitar, apresentar a mesma confirmação sem enviar instruções. [R1–R2]
CA3 — Com e-mail ausente ou inválido, ao enviar, informar a validação e permitir correção. [R1]
CA4 — Com link válido dentro de 60 minutos e conta ativa, ao salvar senha válida com confirmação idêntica, concluir a redefinição. [R2–R3, R5]
CA5 — Com link inválido, expirado ou já utilizado com sucesso, ao tentar redefinir, impedir a alteração e informar o impedimento. [R3]
CA6 — Com um link anterior, após novo envio, ao tentar utilizá-lo, impedir a redefinição; o novo link segue sua própria validade. [R3]
CA7 — Com conta desativada após a emissão, ao tentar usar o link, impedir a redefinição e manter a conta inativa. [R2]
CA8 — Para e-mail cadastrado ou não, ao repetir a solicitação antes de 60 segundos, aplicar o mesmo retorno e espera, sem novo envio. Após o intervalo, permitir nova solicitação. [R4]
CA9 — Com senha fora de qualquer regra de composição, conhecida em vazamentos ou confirmação diferente, ao salvar, recusar a alteração e apresentar a validação. [R5]
CA10 — Com sessões e Lembrar-me em vários dispositivos, ao redefinir com sucesso, invalidar todos esses acessos e retornar ao login; a senha anterior não autentica e a nova permite entrar na conta ativa. [R6–R7]
CA11 — Em desktop e mobile, ao solicitar e redefinir a senha, permitir uso por teclado, com labels, foco visível e mensagens acessíveis de carregamento, validação e resultado. [Fluxos; guia de design]

## Dependências

Contas existentes, envio das instruções por e-mail e retorno ao login existente. Nenhum bloqueador funcional no catálogo aprovado. O e-mail de recuperação está incluído, como exceção às notificações de negócio fora do MVP.

## Designs e evidências

design-recover-password, design-guide e design-login. Decisões Q6–Q10 e confirmação do entendimento registradas em interview.md. O comportamento existente orientou as decisões, sem substituir sua aprovação pelo usuário.

## Dentro do escopo

Solicitação e reenvio, confirmação genérica, envio das instruções, ciclo do link, validação e redefinição da senha, encerramento dos acessos anteriores e retorno ao login. Interface responsiva em português e requisitos explícitos de acessibilidade do guia: contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento. Senhas protegidas e erros sem exposição de dados sensíveis.

## Fora do escopo

Login comum, alteração da senha durante uma sessão, cadastro e reativação administrativa de contas pertencem às respectivas Features. Sem aplicativo nativo, API pública ou integração com sistemas de gestão de projetos.

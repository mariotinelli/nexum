<!-- project-flow:start -->
# [WEB] [PUBLICO] Recuperação de Senha

## Objetivo e resultado esperado
Permitir recuperar a senha da própria conta ativa pela interface WEB responsiva em português, sem revelar se o e-mail está cadastrado. A pessoa recebe instruções, redefine a senha por link válido e retorna ao login; sessões e lembranças anteriores são encerradas.

## Atores e permissões
Pessoas sem sessão podem solicitar recuperação. Somente contas ativas recebem instruções e podem redefinir a senha. A recuperação não reativa contas nem concede permissões.

## Fluxo principal
1. Acessar a recuperação pelo login e informar o e-mail.
2. Acionar Enviar instruções e receber confirmação genérica.
3. Para conta ativa, receber o e-mail e abrir o link válido.
4. Informar Nova senha e Confirmar nova senha; acionar Salvar nova senha.
5. Após validação, salvar a nova senha, encerrar todas as sessões e remover Lembrar-me de todos os dispositivos.
6. Informar sucesso e retornar ao login, sem autenticação automática.

## Regras e exceções
- E-mail obrigatório e válido; confirmação não revela a existência da conta.
- E-mails inexistentes e contas inativas recebem a mesma confirmação, sem envio de instruções.
- Conta desativada após receber o link não pode redefinir a senha enquanto estiver inativa.
- Link válido por 60 minutos desde a emissão, de uso único. Novo envio invalida o anterior.
- Links inválidos, expirados, substituídos ou utilizados não permitem redefinir a senha.
- Intervalo de 60 segundos entre solicitações para o mesmo e-mail, com o mesmo retorno e espera para e-mails cadastrados ou não.
- Nova senha: mínimo de 8 caracteres, maiúscula, minúscula, número e símbolo; rejeitar senhas conhecidas em vazamentos. Confirmação idêntica obrigatória.
- Erros de preenchimento permitem correção; impedimentos no link recebem mensagem acessível. Voltar ao login permanece disponível.

## Critérios de aceite
1. Com conta ativa, solicitar recuperação apresenta confirmação genérica e envia o link; com e-mail inexistente ou conta inativa, apresenta a mesma confirmação sem envio.
2. E-mail ausente ou inválido impede a solicitação e apresenta validação.
3. Com conta ativa, link válido dentro de 60 minutos e senha válida confirmada, salvar conclui a redefinição.
4. Link inválido, expirado, substituído ou já utilizado com sucesso impede alteração da senha e informa o impedimento. Um novo link segue sua própria validade.
5. Desativar a conta após emitir o link impede sua utilização e mantém a conta inativa.
6. Repetir a solicitação antes de 60 segundos aplica o mesmo retorno e espera a e-mails cadastrados ou não, sem novo envio; após o intervalo, permite solicitar novamente.
7. Senha fora de qualquer regra de composição, conhecida em vazamentos ou confirmação diferente impede alteração e apresenta validação.
8. Redefinir com sucesso invalida sessões e Lembrar-me em todos os dispositivos e retorna ao login. A senha anterior não autentica; a nova permite entrar na conta ativa.
9. Em desktop e mobile, solicitação e redefinição são utilizáveis por teclado, com labels, foco visível e mensagens acessíveis de carregamento, validação e resultado.

## Dependências e limites
Utiliza contas existentes, envio das instruções por e-mail e login existente. Nenhum bloqueador funcional no catálogo aprovado. O e-mail de recuperação é uma exceção incluída às notificações de negócio fora do MVP.

Inclui solicitação e reenvio, confirmação genérica, ciclo do link, validação e redefinição da senha, encerramento dos acessos anteriores e retorno ao login. Interface responsiva em português, com contraste WCAG AA, teclado, foco, labels, nomes acessíveis, mensagens descritivas, alvos de toque adequados, hierarquia semântica e redução de movimento. Senhas protegidas e erros sem exposição de dados sensíveis.

Login comum, alteração de senha durante sessão, cadastro e reativação administrativa pertencem às respectivas Features. Sem aplicativo nativo, API pública ou integração com sistemas de gestão de projetos.

## Requisito canônico e evidências
Documento aprovado: docs/harness/features/1014447-recuperacao-de-senha/feature.md
Evidências: design-recover-password, design-guide e design-login. Decisões Q6–Q10 e confirmação do entendimento registradas em interview.md. Requisito aprovado por Mário Tinelli.
<!-- project-flow:end -->
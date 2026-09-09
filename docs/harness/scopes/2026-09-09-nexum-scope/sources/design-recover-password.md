# Source: recuperar-senha.html

- Source ID: `design-recover-password`
- Type: design HTML da tela Recuperar senha
- Origin: C:\Users\maari\Downloads\nexum-scope\design\recuperar-senha.html
- Original SHA-256: `136459c877265c9a5a9456932b72d12fc5ada4a3583e9332eb0b6909e2b44aa3`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Recuperar senha

Tela identificada por `<title>Recuperar senha · Wireframes do MVP</title>` e `PAGE="recuperar-senha"`. No estado inicial solicita o e-mail associado à conta.

## Campos, ações e etapas

- E-mail obrigatório (`type=email`).
- Ação Enviar instruções.
- Link Voltar ao login.
- A query `etapa=redefinir` apresenta Nova senha e Confirmar nova senha, ambas obrigatórias, com ação Salvar nova senha.
- Estados declarados incluem confirmação sem revelar se o e-mail existe, erro por link inválido/expirado e retorno ao login.

## Responsividade e acessibilidade

Contexto compacto em desktop e coluna larga em mobile. Há labels, foco visível, `role=alert`, status ao vivo e texto de erro descritivo. Envio de e-mail e persistência são simulados; nenhuma integração é evidenciada.

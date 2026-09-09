# Source: novo-projeto.html

- Source ID: `design-new-project`
- Type: design HTML da tela Novo projeto
- Origin: C:\Users\maari\Downloads\nexum-scope\design\novo-projeto.html
- Original SHA-256: `9e2573b4b276ab26f191a019177c24641a862ffc59f80d323d6712c60f2d11a2`
- Extraction: análise estática integral de HTML/CSS/JavaScript UTF-8, sem executar conteúdo ativo

## Extracted content

# Novo projeto

Tela identificada por `PAGE="novo-projeto"`. Objetivo: definir dados do projeto e pessoas participantes.

## Campos e ações

- Nome, Identificador e Gestor obrigatórios.
- Descrição, Data inicial e Prazo opcionais.
- Participantes ativos com checkbox e papel Membro/Gestor.
- Texto explícito: “O gestor participa obrigatoriamente do projeto.”
- Ações Cancelar e Criar projeto, com área de erro.

## Comportamento declarado

O gestor selecionado é incluído como participante. O protótipo impede prosseguir sem campos obrigatórios e simula a navegação ao detalhe após criar. Perfis, dados e persistência são simulados; não há evidência de regra para unicidade ou mutabilidade do identificador além de ele ser obrigatório.

## Responsividade e estados

Grade de duas colunas no desktop; campos e papéis empilhados no mobile. Prevê estados loading, vazio, erro e sucesso, labels associados, foco visível e ações com área adequada para toque.

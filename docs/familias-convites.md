# Gestão de famílias — convites por e-mail

Os endpoints exigem autenticação JWT (Authorization: Bearer <token>).

## Criar família

`POST /api/familias/` com `{"nome":"Família Souza"}`.

O criador vira administrador automaticamente. `GET /api/familias/` retorna famílias criadas **ou** das quais o usuário é membro, com listas de `membros` e `despesas`.

## Convidar alguém já cadastrado

`POST /api/familias/{familia_id}/membros/`

```json
{"email":"pessoa@exemplo.com","papel":"membro"}
```

Papel: `membro` ou `dependente`. Somente criador ou administrador pode convidar. A conta deve existir e estar ativa. A inclusão **não acontece imediatamente**: a pessoa precisa aceitar. Convites pendentes duplicados e membros já vinculados retornam HTTP 409.

`GET /api/familias/{familia_id}/convites/` lista convites pendentes do grupo (somente admin).
`DELETE /api/familias/{familia_id}/convites/{convite_id}/` cancela um convite pendente (somente admin).

## Aceitar ou recusar

O usuário convidado consulta `GET /api/familias/convites/` para ver seus convites pendentes.

`POST /api/familias/convites/{convite_id}/responder/` com `{"acao":"aceitar"}` ou `{"acao":"recusar"}`.

Somente o destinatário pode responder; aceitar cria um registro em `MembroFamilia`, enquanto recusar não concede acesso. Convites já respondidos retornam 409.

## Listar integrantes / remover

`GET /api/familias/{familia_id}/membros/` está disponível ao criador e integrantes aceitos.
`DELETE /api/familias/{familia_id}/membros/{membro_id}/` remove integrante (admin) ou permite que ele saia por conta própria.
O criador não pode ser removido.

## Segurança e banco de dados

- Nenhuma rota pública pesquisa usuários por e-mail; somente administradores autenticados podem convidar.
- Não são retornados CPF, senhas, tokens nem dados sensíveis do usuário.
- Família e membros só aparecem para o criador ou usuários com participação aceita.
- A migration `0010_familia_convites_membros` adiciona restrições de unicidade e insere os criadores de famílias antigas como administradores.
- O acesso às informações financeiras da família não altera o acesso individual de cada pessoa às suas transações pessoais.

## Testes

```bash
pdm run python manage.py migrate
pdm run python manage.py test core.tests_familias
pdm run python manage.py test core
```

Esta feature implementa a API, não o formulário/modal do frontend e não envia e-mails externos. Os convites ficam disponíveis para o destinatário quando ele consulta o endpoint autenticado.

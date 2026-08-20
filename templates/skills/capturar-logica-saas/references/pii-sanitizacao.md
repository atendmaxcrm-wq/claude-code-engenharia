# Protocolo de sanitizacao de PII (antes de empacotar)

A captura passa por telas com dado real de cliente/paciente. O PACOTE que vai pra outra VPS
descreve a LOGICA/UX, nao os dados. Este protocolo garante que nenhum nome/CPF/telefone/email
real vaze no zip.

Rodar SEMPRE antes do empacotar.sh (que ate falha se o manifest sanitizado nao existir).

## 1. Manifest

```bash
CAP_ROOT=/root/<slug>-blueprint node scripts/sanitizar-manifest.mjs
```

Remove `navLinks` e `listItems` de cada tela (a sidebar carrega a lista de chat/clientes com
nomes reais). Gera `_recon/manifest-sanitizado.json`. O empacotar.sh so usa esse.

Se algum outro campo carregar PII no seu alvo (ex.: um `selectOptions` com nomes de cliente),
adicionar ao `CAP_PII_DROP` (ex.: `CAP_PII_DROP=navLinks,listItems,selectOptions`).

## 2. Screenshots - revisao MANUAL (o script nao ve imagem)

Passar o olho em `screens/modulos/` e EXCLUIR os shots que mostram dado real:

- [ ] **Listas** de pacientes/clientes/leads (nomes, emails, telefones em coluna).
- [ ] **Modais sobre lista**: o modal em si e limpo, mas o FUNDO mostra a lista. Excluir.
- [ ] **Prontuario / ficha / detalhe de 1 registro** com dado clinico ou pessoal real.
- [ ] **Perfil do dono da conta** (CPF, endereco, dados bancarios).
- [ ] **Financeiro** com valores + nome do pagador real.
- [ ] **Chat / mensagens** com conteudo real.

O que PODE ficar (a UX sem o dado):
- Formularios VAZIOS (campos de "criar X" sem preencher).
- Configuracoes, catalogos, menus, agenda VAZIA, telas de setup.
- Editores com dado de EXEMPLO/placeholder, nao de cliente real.

Dica: capturar preferindo estados VAZIOS (semana de agenda sem compromisso, formulario novo)
ja evita a maioria dos vazamentos na origem.

## 3. Nunca entram no zip

O empacotar.sh ja exclui por construcao, mas conferir que NAO foram parar em screens/ nem no
blueprint:
- [ ] `_recon/_storage-state.json` (cookies/JWT de sessao = acesso).
- [ ] `_recon/_code.txt`, `_recon/_need_code.flag`, `_recon/_watcher.log`, `_recon/_progress.log`.
- [ ] Credenciais IMAP / senha (a nao ser o `ACESSO.md` explicitamente pedido).
- [ ] `net-calls-app.json` com querystrings que embutam dado pessoal (revisar antes de incluir).

## 4. Se o dono pedir a senha no pacote

So entao criar `ACESSO.md` (login + senha + observacao "sensivel, nao commitar/publicar") e
empacotar com `INCLUIR_ACESSO=1`. Avisar no LEIA-ME que o pacote contem credencial.

## Checklist final antes do zip

- [ ] `manifest-sanitizado.json` gerado.
- [ ] screens/ revisado, shots com PII excluidos.
- [ ] blueprint descreve estruturas, nao lista dados reais.
- [ ] nenhum arquivo de sessao/log/codigo em screens/ ou na raiz.
- [ ] decisao sobre ACESSO.md tomada com o dono.

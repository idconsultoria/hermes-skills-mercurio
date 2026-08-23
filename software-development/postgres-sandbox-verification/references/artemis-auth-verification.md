# ArtemisHub — exemplo executado: verificação de gestão de usuários

Reprodução real (2026-08-20, Oracle host ARM64, ambiente sem docker-daemon e sem root).
Prova de conceito do fluxo do skill `postgres-sandbox-verification`.

## Stack do projeto
- Repo `artemishub` (`/opt/data/artemishub`): frontend React/Vite + backend **FastAPI**
  (`backend/main.py`) + **PostgreSQL 17** (restaurado de `db/artemishub.dump`).
- Auth NÃO usa schema `auth` do Supabase: as tabelas vivem no **schema `public`**
  (`public.usuarios`, `public.sessoes`, `public.perfil_usuarios`) — dump do Supabase.
- Hash de senha: `PBKDF2$600000$<salt_hex>$<hash_hex>` (sha256, 600000 iters);
  compatível com formato legado de 5 partes `PBKDF2$iters$SHA256$salt$hash`.
- Master seed: `taciobrito.idteal@gmail.com` (gerencia usuários via papel `master`,
  permissão `usuarios: gerir`). Sessão: tabela `public.sessoes` (token, expira 12h).
- Rotas: `POST /api/auth/login|logout|trocar-senha`, `GET /api/auth/me`,
  `GET|POST /api/usuarios`, `PATCH /api/usuarios/{id}`.

## Como autenticar no teste sem saber a senha do seed
Injete um usuário com hash PBKDF2 conhecido direto no banco, depois logue pela API:
```python
import hashlib, secrets
senha, salt = b"MasterTeste#2026", secrets.token_hex(16)
h = hashlib.pbkdf2_hmac("sha256", senha, bytes.fromhex(salt), 600_000).hex()
stored = f"PBKDF2$600000${salt}${h}"
```
`INSERT INTO public.usuarios (email,nome,senha_hash,papel,ativo,permissoes) VALUES (...)`
com `permissoes` jsonb `{"modulos":{"usuarios":"gerir",...}}`.

## Verificação aplicada (comando de driver em Python via urllib)
1. CRIAR: `POST /api/usuarios` → `201`; linha em `public.usuarios`; usuário criado
   loga (hash válido); senha errada → `401`. ✔ funciona
2. MASTER EDITA SENHA de outro: `PATCH .../usuarios/{id} {"senha":...}` → `200`;
   `senha_hash` atualizado; nova senha loga, antiga → `401`. ✔ funciona
3. DESATIVAR/REATIVAR: `PATCH {"ativo":false}` → `200`, persiste, login bloqueado e
   **sessões ativas invalidadas** (401); `{"ativo":true}` → volta. ✔ funciona
   (proteção "último master ativo" presente via `_checar_ultimo_master`.)
4. APAGAR: `DELETE /api/usuarios/{id}` → **`405 Method Not Allowed`** (só `GET/POST/PATCH`). ✗ GAP
5. CONFIRMAÇÃO DE SENHA na criação: `POST` **sem** `confirmar_senha` → `201` (cria).
   Não há campo no `UsuarioIn` nem no form `src/pages/Usuarios.tsx`. ✗ GAP
6. MOSTRAR/OCULTAR senha: toggle existe no login (`Auth.tsx`) e em alterar-minha-senha
   (`Perfil.tsx`), mas o campo de senha do form "Novo usuário" é fixo
   `type="password"`, sem botão olho. ✗ parcial

## Observações de UX / implementação
- `Usuarios.tsx` usa o ícone `Trash2` (lixeira) para **desativar/reativar** — ambiguidade
  de affordance com "apagar"; não há exclusão real.

## Diretórios de entrega
- Relatório: `/opt/data/entregas/artemis-usuarios-verificacao-v1.html` (identidade ID).
- `/opt/data/deliverables` é root-owned e **sem permissão de escrita** do worker — usar
  `/opt/data/entregas` para versões nomeadas de entregas.
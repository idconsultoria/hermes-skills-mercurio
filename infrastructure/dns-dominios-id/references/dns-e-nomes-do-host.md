# DNS e nomes do host Oracle (ID)

Profundidade da skill `dns-dominios-id`: como provar se um nome existe, separar "sem
registro" de "serviço fora", pedir o registro ao dono da zona e verificar o efeito.

## Inventário — nomes que devem resolver para `129.146.163.107`

| Nome | Serviço | Registro esperado |
|---|---|---|
| `artemis.idconsultoria.ai` | ArtemisHub (produção) | A → 129.146.163.107, TTL 300 |
| `*.artemis.idconsultoria.ai` | preview por PR | A → 129.146.163.107, TTL 300 |
| `treinamentos.idconsultoria.ai` | Moodle da ID | A → 129.146.163.107, TTL 300 |

Zona `idconsultoria.ai` na **Hostinger** (`ns1/ns2.dns-parking.com`). Apex e `www` estão na
Vercel — fora do escopo desta manutenção. Nomes que já apareceram em certificados e **não**
são registros vivos hoje (`atlas`, `dashboard`, `evento`, `manifesto`): só recriar se alguém
confirmar que o serviço existe.

## 1. O nome existe?

Dois provedores independentes, via DoH JSON (só stdlib — não depende de binário de DNS na
máquina):

```python
import json, urllib.request

def doh(name, typ="A"):
    out = {}
    for prov, base in (("cloudflare", "https://cloudflare-dns.com/dns-query"),
                       ("google", "https://dns.google/resolve")):
        req = urllib.request.Request(f"{base}?name={name}&type={typ}",
                                     headers={"accept": "application/dns-json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
        out[prov] = (d.get("Status"), [a.get("data") for a in d.get("Answer", [])])
    return out   # Status 3 = NXDOMAIN (nome não existe)
```

`scripts/verificar-dns-id.py` roda esse laço sobre o inventário e sai com código ≠ 0 no
primeiro nome que não devolve o IP esperado. Rodar antes de qualquer diagnóstico de
"aplicação quebrada" — e periodicamente, para pegar registro sumido no mesmo dia.

Um provedor só não basta: cache negativo e caches regionais divergem por minutos.

## 2. "Sem registro" ou "serviço fora"?

```bash
# do lado de fora (fala com o NPM pelo IP do host, ignorando o DNS)
curl -sk --resolve <nome>:443:129.146.163.107 -o /dev/null -w '%{http_code}\n' https://<nome>/

# do lado do host (NPM em loopback)
curl -sk --resolve <nome>:443:127.0.0.1 -o /dev/null -w '%{http_code}\n' https://<nome>/
```

- `200`/`303` → NPM, certificado e container servindo: falta só o registro.
- `000` → a conexão não completou; se o nome resolve, desconfie do certificado (preview sem
  PR aberto não tem cert emitido) ou do proxy host.

Assinaturas úteis: `303 → /login/index.php` com `x-powered-by: PHP` identifica o Moodle; HTML
pequeno com a SPA do ArtemisHub identifica o frontend.

## 3. O que NÃO prova registro vivo

- **crt.sh / transparência de certificados**: lista nomes que tiveram certificado. Registro
  removido continua aparecendo ali por meses — nunca apresentar essa lista como "conteúdo da
  zona".
- **Wildcard em certificado antigo** (`*.idconsultoria.ai`): não implica wildcard na zona.
- **"o site abre aqui"**: no navegador de quem já visitou, é o cache do PWA/site antigo.

## 4. Pedir o registro ao dono da conta (painel Hostinger)

Um registro por linha, campos exatos:

| Tipo | Nome | Aponta para | TTL |
|---|---|---|---|
| A | `artemis` | 129.146.163.107 | 300 |
| A | `*.artemis` | 129.146.163.107 | 300 |
| A | `treinamentos` | 129.146.163.107 | 300 |

Passo a passo que se envia ao dono: hpanel.hostinger.com → **Domínios** → `idconsultoria.ai`
→ aba **DNS / Nameservers** → **Adicionar registro** → preencher → salvar.

- TTL só muda a rapidez com que o mundo enxerga a mudança; se o painel não aceitar 300, o
  menor disponível serve.
- O wildcard **não** cobre o nome puro: `artemis` e `*.artemis` são registros distintos.
- **Não** mexer em nameservers nem no apex/`www` (Vercel).
- Autoria da mudança: pedir ao suporte (chat 24 h) o **histórico de alterações da zona** — o
  DNS em si não guarda quem alterou.

## 5. Verificação pós-mudança (o que autoriza dizer "resolvido")

1. Resolução em 2 provedores, após alguns minutos (cache negativo do NXDOMAIN = SOA minimum,
   ~600 s).
2. `https://artemis.idconsultoria.ai/` → 200 e `/api/health` → `{"status":"ok"}`.
3. Hash do build servido == hash no container:

   ```bash
   curl -sk -o /tmp/served.js https://artemis.idconsultoria.ai/assets/index-<hash>.js
   md5sum /tmp/served.js
   ssh ... 'docker exec artemishub-frontend md5sum /usr/share/nginx/html/assets/index-*.js'
   ```

   Hash igual = o que está no ar é o build do host (com os fixes), não o cache do usuário.
4. `treinamentos.idconsultoria.ai/login/index.php` → 200 (Moodle de volta).
5. Preview: nome resolve; erro de TLS sem PR aberto é esperado.
6. Avisar o usuário da **recarga forçada** (Ctrl+Shift+R; no celular, fechar e reabrir o app).

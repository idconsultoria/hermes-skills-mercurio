# agy Session Audit — Protobuf Extraction Reference

> Scripts e técnica para extrair token usage de sessões do agy (Google Antigravity CLI).
> As sessões ficam em SQLite DBs com blobs protobuf — sem schema público.

## Schema Protobuf (via engenharia reversa)

Schemas extraídos por terceiros:

- **`jkfujinami/antigravity-grpc-schemas`** — Schemas gRPC/Protobuf completos do Antigravity v2.0 (MIT). Contém `trajectory.proto`, `cortex.proto`, `codeium_common.proto`.
- **`ag-donald/Antigravity-Database-Manager`** — Schema da trajectory no `state.vscdb` do IDE.

## Hierarquia de Extração de Tokens

```
CortexStepGeneratorMetadata (blob da tabela gen_metadata)
  └── field 1 → ChatModelMetadata (oneof: chat_model)
       ├── field 3 → model (enum)
       └── field 4 → ModelUsageStats
            ├── field 2 → input_tokens (uint64)
            ├── field 3 → output_tokens (uint64)
            ├── field 4 → cache_write_tokens (uint64)
            ├── field 5 → cache_read_tokens (uint64)
            ├── field 9 → thinking_output_tokens (uint64)
            └── field 10 → response_output_tokens (uint64)
```

## Modelos Reais (via `agy models`)

Não confiar nos enums do proto — os valores internos 1016, 1020 são modelos mais recentes que o schema público:

| Enum DB | Nome real (agy models) |
|---------|------------------------|
| 1016 | Gemini 3.5 Flash |
| 1020 | Gemini 3.1 Pro |

## Script de Extração Completo (Python)

```python
import sqlite3, glob, os

HOME = os.path.expanduser("~")
DBS = sorted(glob.glob(os.path.join(HOME, ".gemini/antigravity-cli/conversations/*.db")))

def dv(data, offset):
    r = 0; s = 0
    while offset < len(data):
        b = data[offset]; r |= (b & 0x7F) << s; s += 7; offset += 1
        if not (b & 0x80):
            if r > 0x7FFFFFFFFFFFFFFF: r -= 0x10000000000000000
            return r, offset
    return None, offset

def parse_session(dbpath):
    """Extract usage stats from one agy conversation DB"""
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    cur.execute("SELECT idx, data, size FROM gen_metadata ORDER BY idx")
    gen_rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM steps")
    steps = cur.fetchone()[0]
    
    si = so = scr = scw = sthink = sresp = 0
    model_id = 0
    
    for idx, blob, sz in gen_rows:
        if not blob or len(blob) < 20: continue
        i = 0
        while i < len(blob):
            if i >= len(blob): break
            key = blob[i]; fn = key >> 3; wt = key & 0x07; i += 1
            if wt == 2 and fn == 1:  # chat_model
                length, i2 = dv(blob, i)
                if length is None or i2 + length > len(blob): break
                cm = blob[i2:i2+length]; i = i2 + length
                j = 0
                while j < len(cm):
                    ck = cm[j]; cf = ck >> 3; cw = ck & 0x07; j += 1
                    if cw == 0:
                        cv, j = dv(cm, j)
                        if cv is None: break
                        if cf == 3 and 1 <= cv <= 10000: model_id = cv
                    elif cw == 2 and cf == 4:  # usage
                        ulen, ustart = dv(cm, j)
                        if ulen is None or ustart + ulen > len(cm): break
                        ud = cm[ustart:ustart+ulen]; j = ustart + ulen
                        k = 0
                        while k < len(ud):
                            uk = ud[k]; uf = uk >> 3; uw = uk & 0x07; k += 1
                            if uw == 0:
                                uv, k = dv(ud, k)
                                if uv is None: break
                                if uv < 0 or uv > 100_000_000: continue
                                if uf == 2: si += uv
                                elif uf == 3: so += uv
                                elif uf == 4: scw += uv
                                elif uf == 5: scr += uv
                                elif uf == 9: sthink += uv
                                elif uf == 10: sresp += uv
                            elif uw == 2:
                                sl, sk = dv(ud, k)
                                if sl and sk + sl <= len(ud): k = sk + sl
                                else: break
                            elif uw == 5: k += 4
                            elif uw == 1: k += 8
                    elif cw == 2:
                        sl, sk = dv(cm, j)
                        if sl and sk + sl <= len(cm): j = sk + sl
                        else: break
            elif wt == 2:
                length, i2 = dv(blob, i)
                if length is None or i2 + length > len(blob): break
                i = i2 + length
            elif wt == 0:
                val, i = dv(blob, i)
                if val is None: break
            elif wt == 5: i += 4
            elif wt == 1: i += 8
    
    conn.close()
    return si, so, scr, scw, sthink, sresp, model_id, steps, len(gen_rows)

MODEL_MAP = {
    1: "gemini-2.0-flash", 2: "gemini-2.5-pro",
    1016: "gemini-3.5-flash", 1020: "gemini-3.1-pro",
}

# Usage:
# for dbpath in DBS:
#     si, so, scr, scw, sth, sre, mid, steps, gen = parse_session(dbpath)
#     model = MODEL_MAP.get(mid, f"model_{mid}")
```

## Notas

- O `model` é extraído do campo 3 de `ChatModelMetadata` (enum varint), NÃO de string
- Os enums 1016 e 1020 **não estão** no schema público — foram descobertos empiricamente
- Token counts podem ter valores negativos se o varint for lido como unsigned — usar signed conversion (`if r > 0x7FFFFFFFFFFFFFFF: r -= 0x10000000000000000`)
- A maioria das sessões tem 2+ gen_metadata entries; somar todos para o total da sessão
- As 85 DBs ocupam ~35 MB no total (~400 KB cada em média)

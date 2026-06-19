# Deploy Vulcano (or Custom MCP Service) on Oracle Host

Deploying a Docker-based MCP service with a custom vault adapter, connecting it to
Hermes via the `ai_mesh` network. Documented from the Vulcano v3.0 deployment on
19 Jun 2026 (AumentacaoAdapter for 97 solution files).

## Architecture

```
Hermes Container (ai_mesh 172.19.0.7)
  │ mcp_client → http://vulcano:8765/sse
  │              (DNS via ai_mesh network)
  ▼
Vulcano Container (ai_mesh 172.19.0.12)
  ├── redis (cache)
  ├── mcp_server.py (FastMCP SSE)
  │   └── AumentacaoAdapter (custom VaultAdapter)
  └── FAISS index (97 vectors)
```

## Step-by-Step

### 1. Clone the Repo
```bash
ssh oracle-host 'git clone https://github.com/nosterviz/vulcano ~/.vulcano'
```

### 2. Study the Adapter Pattern
The adapter system lives in `engine/adapters/`:
- `base.py` — abstract `VaultAdapter` class (10 methods: resolve, read_engram,
  follow_links, search_engrams, list_clusters, list_engrams, get_mode_context,
  read_project_state, write_engram, load_engrams)
- `hephaistos.py` — for Hephaistos vaults (engramas/ + projetos/ structure)
- `masonry.py` — for flat doc vaults with cluster dirs

### 3. Create a Custom Adapter
Write your adapter locally, scp it to the host, then inject into the container:
```bash
# Write adapter locally
write_file /tmp/my_adapter.py

# Copy to host, then to container (if already built)
scp /tmp/my_adapter.py oracle-host:~/.vulcano/engine/adapters/my_adapter.py
docker cp ~/.vulcano/engine/adapters/my_adapter.py vulcano-vulcano-1:/app/engine/adapters/
```

**Key adapter methods to implement:**
- `load_engrams()` — returns `Dict[str, Dict]` with keys: path, content, size,
  wikilinks, first_line. This is what FAISS indexes.
- `list_clusters()` — returns `{cluster_name: count}` for search filtering
- `resolve(name)` — Path resolution for read_engram tool

### 4. Register the Adapter in mcp_server.py
Patch `_build_adapter()` in `engine/mcp_server.py`:
```python
elif ADAPTER == "my_adapter":
    from engine.adapters.my_adapter import MyAdapter
    return MyAdapter(VAULT_PATH)
```

### 5. ⚠️ Patch batch_indexer.py (Critical Pitfall)
The `scripts/batch_indexer.py` does NOT read the ADAPTER env var and does NOT
pass an adapter to VulcanoEngine. It defaults to VulcanoVault which only scans
`engramas/` directories. You MUST patch it to support your adapter:

```python
ADAPTER = os.environ.get("ADAPTER", "hephaistos").lower()

_adapter = None
if ADAPTER == "my_adapter":
    from engine.adapters.my_adapter import MyAdapter
    _adapter = MyAdapter(VAULT_PATH)
# ... other adapters

engine = VulcanoEngine(..., adapter=_adapter)
```

### 6. Configure Docker Compose
```yaml
services:
  vulcano:
    build: .
    ports:
      - "${MCP_PORT:-8765}:8765"
    volumes:
      - /path/to/vault:/vault:ro
      - faiss_data:/app/faiss
    environment:
      - VAULT_PATH=/vault
      - ADAPTER=my_adapter
      - REDIS_URL=redis://redis:6379
    networks:
      default:
        name: ai_mesh
        external: true
```

**ARM64 note:** `FROM python:3.11-slim` is multi-arch and works natively on
Oracle Ampere (ARM64). All pip packages (faiss-cpu, sentence-transformers,
torch) have ARM64 wheels — no QEMU needed. The build takes ~3-5 min on first
run (2.6GB of dependencies).

### 7. Build, Deploy, Index
```bash
cd ~/.vulcano
docker compose up -d

# Index the vault (after patching batch_indexer.py)
# Copy patched file into container first:
docker cp ~/.vulcano/scripts/batch_indexer_v2.py vulcano-vulcano-1:/app/scripts/
docker exec vulcano-vulcano-1 python3 /app/scripts/batch_indexer_v2.py
```

### 8. Connect to Hermes (config.yaml, NOT CLI)
**Do NOT use `hermes mcp add`** for SSE MCP servers — it POSTs to `/sse`
which returns 405 (SSE only accepts GET). Instead, edit config.yaml directly:

```python
# Inside the Hermes container:
python3 -c "
import yaml
with open('/opt/data/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
config.setdefault('mcp_servers', {})
config['mcp_servers']['vulcano'] = {
    'url': 'http://vulcano:8765/sse',
    'timeout': 180,
    'connect_timeout': 30,
}
with open('/opt/data/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
"
```

### 9. Activate
Ask the user to type `/reload-mcp` in-session. The new MCP server's tools
become available without restarting Hermes. Verify with:
```bash
hermes tools list | grep vulcano
```

### 10. Verify Search Works
```bash
# From Hermes container:
docker exec hermes_agent curl -s --connect-timeout 5 http://vulcano:8765/sse
# (connection will hang — SSE is streaming. That's normal.)

# Run a semantic search test:
docker exec vulcano-vulcano-1 python3 -c "
from engine.vulcano_v2 import VulcanoEngine
from engine.adapters.my_adapter import MyAdapter
engine = VulcanoEngine('/vault', adapter=MyAdapter('/vault'))
engine._load_engrams()
engine.build_index()
results = engine.vector_search('natural language query here', top_k=5)
for eid, score in results:
    print(f'{score:.3f} | {engine.engrams[eid][\"path\"]} | {engine.engrams[eid][\"first_line\"][:60]}')
"
```

## Verification Checklist
- [ ] `docker compose ps` shows both redis + vulcano containers healthy
- [ ] `docker logs vulcano-...` shows "Uvicorn running on http://0.0.0.0:8765"
- [ ] Batch indexer reports N>0 engrams and N>0 FAISS vectors
- [ ] Hermes config.yaml contains the MCP server entry
- [ ] `/reload-mcp` succeeds without errors
- [ ] `hermes tools list` shows vulcano tools (search, read_engram, etc.)

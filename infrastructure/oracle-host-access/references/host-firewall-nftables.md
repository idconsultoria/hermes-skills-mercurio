# Oracle Cloud — Dual Firewall

O servidor Oracle tem **duas camadas independentes** de firewall:

```
1. Oracle Cloud Security List (hipervisor/VNIC level)
   └── Bloqueia antes do tráfego chegar no sistema
2. Host nftables/iptables (kernel level)
   └── Filtra o que chega nas interfaces de rede
```

## Problema

Uma porta pode estar aberta no host mas bloqueada no Security List → **connection timed out** de fora.
OU uma regra `nft add rule` pode ser adicionada após o `reject` catch-all e nunca ser executada.

## Verificação

```bash
# De dentro do servidor: porta está ouvindo?
ss -tlnp | grep <port>

# De fora: Security List está bloqueando?
# (Não use nc do próprio servidor — hairpin NAT não funciona em clouds)
# Use portchecker.co ou yougetsignal.com no navegador
```

## Solução

### 1. Abrir no host (nftables)

⚠️ **`nft add rule` APPENDS ao fim da chain.** Se existe um `reject with icmp type host-prohibited` (catch-all) antes, a regra nunca é alcançada. Use `insert` (prepend) em vez de `add` (append):

```bash
# CERTO — insert no início, antes de qualquer reject
sudo nft insert rule ip filter INPUT tcp dport <port> accept

# Também funciona (iptables-nft, insere na posição 1)
sudo iptables -I INPUT -p tcp --dport <port> -j ACCEPT

# ERRADO — append depois do reject, nunca executado
# sudo nft add rule ip filter INPUT tcp dport <port> accept
```

Para ver a chain completa e confirmar a ordem:
```bash
sudo nft list chain ip filter INPUT
# Ou iptables:
sudo iptables -L INPUT -n -v
```

### 2. Abrir no Oracle Cloud Console
```
Rede → Virtual Cloud Network → Security List → Ingress Rules
Source: 0.0.0.0/0
Protocol: TCP
Destination Port: <port>
```

## Diagnostic Approach (this session's pattern)

Quando o usuário reporta "não consigo acessar do navegador":

1. Teste local com Host header correto:
   ```bash
   ssh oracle-host 'curl -s -H "Host: <public-ip>" http://localhost/ | head -c 200'
   ```

2. Verifique NPM proxy hosts:
   ```bash
   ssh oracle-host 'docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite'
   ssh oracle-host 'python3 -c "
   import sqlite3
   c = sqlite3.connect(\"/tmp/npm.sqlite\").cursor()
   c.execute(\"SELECT id, domain_names, forward_host, forward_port FROM proxy_host\")
   for r in c.fetchall(): print(r)
   "'
   ```

3. Verifique Docker networks — NPM e target precisam estar na mesma rede bridge:
   ```bash
   ssh oracle-host 'docker inspect nginx_proxy_manager --format "{{json .NetworkSettings.Networks}}"'
   ssh oracle-host 'docker inspect taskflow-nginx --format "{{json .NetworkSettings.Networks}}"'
   ```

4. Verifique de fora com port checker (portchecker.co) — se "closed" mesmo com tudo certo no host, é o Security List.

## Portas atualmente abertas

| Porta | Serviço | Security List | nftables |
|-------|---------|--------------|----------|
| 22 | SSH | ✅ | ✅ |
| 80 | HTTP (NPM) | ✅ | ✅ |
| 81 | NPM Admin | ✅ | ✅ |
| 443 | HTTPS (NPM) | ✅ | ✅ |
| 9119 | Hermes Dashboard | ✅ | ✅ |
| 8642 | Hermes API | ✅ | ✅ |
| 2222 | Pi Agent SSH | ❌ | ✅ |

Porta 2222 está liberada no nftables (host) mas **falta liberar no Security List** via Oracle Cloud Console.

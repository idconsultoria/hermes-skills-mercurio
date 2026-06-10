# Gateway Troubleshooting

## Gateway won't start / messenger platforms silent

### 1. Check config migration aftermath

After a `hermes config migrate` (schema version bump), diff against the backup:

```bash
diff /opt/data/config.yaml /opt/data/config.yaml.bak-20260605T213438Z
```

**Sections that got dropped in v26→v27:**
- `platform_toolsets` — maps each messenger platform to its toolset (`hermes-telegram`, `hermes-discord`, …). Without it the gateway loads no platform toolsets and no platform can process messages.
- `mcp_servers` — MCP server definitions (e.g. Notion) are lost.
- `session_reset` — session reset config lost (non-critical).
- `plugins` — plugin definitions lost.

Always restore these after a migration:

```bash
# platform_toolsets — use Python + yaml, NOT `hermes config set`
# (hermes config set stores JSON arrays as quoted YAML strings)
python3 -c "
import yaml
with open('/opt/data/config.yaml') as f:
    data = yaml.safe_load(f)
data['platform_toolsets'] = {
    'cli': ['hermes-cli'],
    'discord': ['hermes-discord'],
    'google_chat': ['hermes-google_chat'],
    'homeassistant': ['hermes-homeassistant'],
    'qqbot': ['hermes-qqbot'],
    'signal': ['hermes-signal'],
    'slack': ['hermes-slack'],
    'teams': ['hermes-teams'],
    'telegram': ['hermes-telegram'],
    'whatsapp': ['hermes-whatsapp'],
    'yuanbao': ['hermes-yuanbao'],
}
with open('/opt/data/config.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
"
```

**Pitfall:** `yaml.dump()` reorders the file to Python dict insertion order. Keys may end up in a different order than hermes config expects. Run `hermes config check` after to confirm no structural errors.

### 2. Check s6 supervision state

The gateway runs as an s6 longrun service. It can be marked `down` (blocked from auto-starting):

```bash
# Check service status
s6-svstat /run/service/gateway-default

# If it shows "down" or "normally down"
ls -la /run/service/gateway-default/down   # ← this file exists when service is intentionally down

# Bring it up
/package/admin/s6-2.15.0.0/command/s6-svc -u /run/service/gateway-default
```

**Finding s6-svc:** It's usually not on PATH. Locate it:
```bash
find / -name 's6-svc' -type f 2>/dev/null
```

### 3. Read both log streams

The gateway writes logs to **two locations** — check both:

```bash
# Direct file logging (older / container-level)
tail -50 /opt/data/logs/gateway.log

# s6-log pipe (current run's stdout)
tail -30 /opt/data/logs/gateways/default/current
```

The s6-log file (`current`) is the authoritative stream for the running gateway process. The direct file (`gateway.log`) may be from a previous run.

### 4. Verify platform_toolsets is structured correctly

`hermes config set platform_toolsets.X '["hermes-X"]'` stores the value as a **YAML string** (`["hermes-X"]` quoted), not a YAML list. This breaks gateway toolset discovery.

Check:
```bash
grep -A 2 'telegram:' /opt/data/config.yaml
```

If value starts with `'[` it's broken. Fix with the Python yaml approach above.

### 5. Common gateway log patterns

| Log line | Meaning |
|----------|---------|
| `✓ telegram connected` | Telegram working |
| `✓ whatsapp connected` | WhatsApp bridge ready |
| `Refusing to start: API_SERVER_KEY is required` | Harmless — API server not needed |
| `✗ whatsapp error: ... connect timed out` | Bridge npm install may be taking longer |
| `Unauthorized user: ... on whatsapp` | User not in ALLOWED_USERS |
| `Channel directory built: 0 target(s)` | No home channel set — `/sethome` from the target platform |
| `down` file in service dir | s6 blocked auto-start (restart artifact) |
| `Fatal ... adapter error` | Bridge process died — may auto-reconnect |

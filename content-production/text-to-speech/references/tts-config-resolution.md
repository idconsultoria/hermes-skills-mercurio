# TTS Config Resolution — Debug Log

## The two-config trap

This environment has **two** config files with different `tts.provider` values:

| File | Provider | Size |
|------|----------|------|
| `/opt/data/config.yaml` | `omnivoice` | 16.5 KB |
| `/opt/data/.hermes/config.yaml` | `hermes-tts` | 239 B |

Only the **first** is loaded by the TTS tool, because `HERMES_HOME=/opt/data` and
`get_config_path()` = `get_hermes_home() / "config.yaml"`.

The `.hermes/` subdirectory config is a red herring — Hermes never looks there
for the main config. It exists because `~/.hermes/config.yaml` is the
*platform-default* path (when `HERMES_HOME` is unset), but here `HERMES_HOME`
overrides it.

## Resolution chain (from `/opt/hermes/tools/tts_tool.py`)

```
text_to_speech_tool()
  → _load_tts_config()          # calls load_config() from hermes_cli.config
    → load_config()              # get_config_path() = <HERMES_HOME>/config.yaml
    → _get_provider(config)      # tts_config.get("provider") or "edge"
  → _resolve_command_provider_config(provider, config)
    → if provider in BUILTIN_TTS_PROVIDERS → None (use native handler)
    → else → lookup tts.providers.<name> → if type:command → return config
    → else → None
  → if command_provider_config:
      _generate_command_tts()
  → elif provider not in builtins and plugin:
      _dispatch_to_plugin_provider()
  → elif provider == "elevenlabs" / "openai" / etc:
      native handler
  → else:
      Edge TTS default
```

## BUILTIN_TTS_PROVIDERS (hardcoded set)

```python
BUILTIN_TTS_PROVIDERS = frozenset({
    "edge", "elevenlabs", "openai", "minimax", "xai",
    "mistral", "gemini", "neutts", "kittentts", "piper",
})
```

Any provider name NOT in this set → resolved as command provider from
`tts.providers.<name>`.

## Omnivoice command provider (in main config)

```yaml
tts:
  provider: omnivoice
  providers:
    omnivoice:
      type: ''                         # ← empty string, not "command"
      command: python3 /opt/data/.hermes/scripts/omnivoice-tts.py --text-file {input_path}
        --output {output_path} --voice {voice} --model {model}
      output_format: wav
      timeout: 300
      voice: female
      model: omnivoice
```

Note `type: ''` — a non-empty `type` that isn't `"command"` causes
`_is_command_provider_config` to return `False`. An empty string is treated
as "not set" (the check is `ptype and ptype != "command"`), so it still
resolves. This is a latent footgun if someone sets `type: script` or similar.

## Omnivoice script

`/opt/data/.hermes/scripts/omnivoice-tts.py` — bridges to OmniVoice API at
`http://omnivoice-api:8880/v1/audio/speech`. Fails with exit code 1 + "Error:"
on the stderr when curl cannot reach the endpoint (container not running or
DNS resolution failure across Docker networks).

## Key takeaway

**Always check `$HERMES_HOME/config.yaml`** when the TTS tool uses an unexpected
provider. The config in `.hermes/config.yaml` is a secondary artifact from
`hermes setup` runs — it's loaded only when `HERMES_HOME` is unset and the
platform default kicks in.

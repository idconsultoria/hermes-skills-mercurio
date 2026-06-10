# agy Setup — Session Reference

## Install Locations (gustavo-oracle-server-vnic)

| Location | Binary Path | Version |
|---|---|---|
| Host (Oracle VM) | `/home/ubuntu/.local/bin/agy` | 1.0.5 |
| Hermes container | `/opt/data/home/.local/bin/agy` | 1.0.5 |

## PATH Setup

**Host:** Auto-added by installer to `~/.bashrc` and `~/.profile`

**Container:** Add manually:
```bash
export PATH="/opt/data/home/.local/bin:$PATH"
```

## Authentication State

**NOT AUTHENTICATED.** First run prints:
```
Authentication required. Please visit the URL to log in:
  https://accounts.google.com/o/oauth2/auth?access_type=offline&client_id=...
```

User must open URL in browser. Credentials stored in Linux Secret Service / dbus keyring (headless server may fall back to local file).

## OAuth Client Details

- Client ID: `1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com`
- Scopes: cloud-platform, userinfo.email, userinfo.profile, cclog, experimentsandconfigs, openid
- Redirect URI: `https://antigravity.google/oauth-callback`
- Token storage: OS keyring (Secret Service/dbus) on Linux

## Commands Tested

```bash
agy --version     # → 1.0.5
agy doctor        # → "Authentication required" (expected, not yet authed)
```

## Next Steps for User

1. Open the OAuth URL in browser
2. Authenticate with Google account
3. Verify with `agy doctor`
4. Test design workflow: `agy /goal "Create a landing page mockup"`

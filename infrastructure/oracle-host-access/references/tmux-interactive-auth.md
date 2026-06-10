# tmux — Interactive CLI Auth on Headless Servers

Many CLI tools (agy, gcloud, gh, etc.) need a real PTY/TTY for OAuth flows. When running via SSH from inside a container (no local TTY), `tmux` creates a persistent pseudo-terminal on the host that survives SSH disconnects and supports keyboard input.

## When to Use This Pattern

- A CLI tool prints an OAuth URL and expects the user to paste an auth code back
- The binary crashes with `"could not open TTY"` or `"not a terminal"` when run non-interactively
- The tool uses bubbletea or similar TUI frameworks (termbox, tcell, promptui)
- You need to interact with a CLI that has arrow-key menus, select prompts, or multi-step wizards

## Step-by-step

### 1. Install tmux on the host
```bash
ssh oracle-host 'sudo apt-get install -y -qq tmux'
```

### 2. Create a named session with the CLI running
```bash
ssh oracle-host 'tmux new-session -d -s <session-name> "env HOME=/home/ubuntu TERM=xterm-256color /path/to/cli"'
```

Key flags:
- `-d` — detached (runs in background)
- `-s <name>` — human-friendly session name
- The command string after the session name is what runs inside tmux
- Pass `HOME`, `TERM`, and `PATH` explicitly — tmux may not inherit the SSH environment

### 3. Read the output (capture pane)
```bash
ssh oracle-host 'tmux capture-pane -t <session-name> -p -S -30'
```
- `-p` — print to stdout instead of clipboard
- `-S -30` — last 30 lines of scrollback. Use `-S -100` for more context

### 4. Send menu selections (arrow keys, Enter)
```bash
ssh oracle-host 'tmux send-keys -t <session-name> "1" Enter'
ssh oracle-host 'tmux send-keys -t <session-name> Down Down Enter'
```

Text keys:
```bash
ssh oracle-host 'tmux send-keys -t <session-name> "the-auth-code-pasted-here" Enter'
```

### 5. Kill the session when done
```bash
ssh oracle-host 'tmux send-keys -t <session-name> C-c'
ssh oracle-host 'tmux send-keys -t <session-name> "exit" Enter'
ssh oracle-host 'tmux kill-session -t <session-name>'
```

## Reusable Auth Flow (agy example)

```bash
# 1. Create session
ssh oracle-host 'tmux new-session -d -s agy-auth \
  "env HOME=/home/ubuntu TERM=xterm-256color /home/ubuntu/.local/bin/agy"'

# 2. Wait for UI to render, capture URL
sleep 3
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -30'

# 3. Select auth method (e.g., option "1" for Google OAuth)
ssh oracle-host 'tmux send-keys -t agy-auth "1" Enter'

# 4. Capture again to get the full OAuth URL
sleep 2
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -20'

# 5. Extract URL from output, give to user
# 6. User authenticates in browser, returns auth code

# 7. Paste the code into the running agy session
ssh oracle-host 'tmux send-keys -t agy-auth "4/0XXXXXXXXXXXXXXXXXXXX" Enter'

# 8. Wait for auth to complete, verify
sleep 3
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -10'
# Expected: "Welcome to Antigravity CLI!" or similar success message

# 9. Cleanup
ssh oracle-host 'tmux send-keys -t agy-auth C-c'
sleep 1
ssh oracle-host 'tmux kill-session -t agy-auth'
```

## Pitfalls

⚠️ **tmux command not found?** Install: `sudo apt-get install -y tmux`

⚠️ **CLI crashes inside tmux?** The most common cause is missing `HOME` or `PATH`. Always pass `env HOME=/home/ubuntu PATH=/home/ubuntu/.local/bin:/usr/bin:/bin` in the command string.

⚠️ **Pane output is truncated?** The URL may span multiple lines in tmux (word-wrapped). Use `capture-pane -S -50` to get more scrollback. Reconstruct the URL by joining split lines (they wrap at terminal width, ~80-120 chars).

⚠️ **send-keys sends literal text not key events?** `send-keys` types text as if the user typed it. For control characters, use `C-c`, `C-d`, `C-z`. For special keys, use `Tab`, `Down`, `Up`, `Enter`, `Escape`, `Backspace`.

⚠️ **Session died before auth completed?** Check `tmux list-sessions` to confirm it's still running. If killed, recreate the session — the OAuth URL changes on each run (new PKCE challenge).

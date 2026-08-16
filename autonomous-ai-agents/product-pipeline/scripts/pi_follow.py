#!/usr/bin/env python3
"""
pi_follow.py — Acompanha uma sessão Pi Agent ao vivo, com formatação legível.

Uso:
    python3 pi_follow.py [caminho_do_jsonl] [--replay]
    python3 pi_follow.py --replay          # pega a sessão mais recente e mostra o histórico

Não escreve no arquivo — apenas lê (seguro com jobs em background). Substitui o
`tail -f` cru do JSONL, que é ilegível.

Formato real do JSONL (Pi Agent v0.78):
- type=message com message.content = lista de blocos:
    {type: "thinking", thinking: "..."}     → raciocínio (dimm)
    {type: "text", text: "..."}             → fala (assistant) / input (user) / saída (toolResult)
    {type: "toolCall", id, name, arguments} → tool call DENTRO do content
  toolResult também é message com role=toolResult e content text (tool em toolName)

Pitfalls embutidos:
- NÃO usar expanduser("~") — quando invocado via `docker exec` sem `-u`, o HOME vira /root
  e as sessões do usuário hermes ficam em /opt/data/home/.pi/... → usar caminho absoluto.
- `docker exec -it` falha do PowerShell/SSH (sem TTY alocado: "cannot attach stdin to a
  TTY-enabled container") → usar `docker exec` SEM `-it` para scripts read-only.
- `--replay` precisa ser filtrado antes do path posicional (senão vira argv[1]).

Exemplo de invocação do host Oracle (PowerShell):
    ssh ubuntu@<host> "docker exec hermes_agent python3 /opt/data/scripts/pi_follow.py --replay"
"""
import json
import os
import sys
import time
import glob

CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
RED = "\033[91m"; MAGENTA = "\033[95m"; DIM = "\033[2m"
BOLD = "\033[1m"; RESET = "\033[0m"

# Absoluto (não ~): docker exec sem -u roda como root e ~ aponta errado.
SESSIONS_DIR = os.environ.get(
    "PI_FOLLOW_DIR",
    "/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-cfp-ia--/",
)


def newest_session():
    files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def short(s, n=150):
    s = str(s)
    return s if len(s) <= n else s[:n] + "…"


def cmd_from_args(args):
    if not isinstance(args, dict):
        return short(args, 100)
    if args.get("command"):
        return str(args["command"])[:100]
    if args.get("code"):
        return str(args["code"])[:100]
    if args.get("prompt"):
        return str(args["prompt"])[:100]
    if args.get("path"):
        return f"→ {args['path']}"
    if args.get("url"):
        return f"→ {args['url']}"
    return short(args, 100)


def render(e):
    ts = (e.get("timestamp") or "")[11:19]
    if e.get("type") != "message":
        if e.get("type") == "session_info":
            return f"{DIM}{ts}{RESET} {BOLD}⛁ sessão: {e.get('name','')}{RESET}"
        if e.get("type") == "model_change":
            return f"{DIM}{ts}{RESET} {MAGENTA}◇ modelo: {e.get('modelId','?')} ({e.get('provider','?')}){RESET}"
        return None

    m = e.get("message", {})
    role = m.get("role", "?")
    blocks = m.get("content", [])
    if not isinstance(blocks, list):
        blocks = [{"type": "text", "text": str(blocks)}]

    out_lines = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        bt = b.get("type")
        if bt == "thinking":
            txt = str(b.get("thinking", "")).strip()
            if txt:
                out_lines.append(f"{DIM}   …{short(txt, 110)}{RESET}")
        elif bt == "toolCall":
            name = b.get("name", "tool")
            args = b.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    pass
            cmd = cmd_from_args(args)
            out_lines.append(f"{BOLD}{GREEN}⚙ {name}{RESET} {DIM}{cmd}{RESET}")
        elif bt == "text":
            txt = str(b.get("text", "")).strip()
            if txt:
                if role == "assistant":
                    out_lines.append(f"{CYAN}▌assistant{RESET} {short(txt, 180)}")
                elif role == "user":
                    out_lines.append(f"{YELLOW}▌user{RESET} {short(txt, 180)}")
                elif role == "toolResult":
                    err = b.get("isError") or m.get("isError")
                    color = RED if err else DIM
                    tag = "✗" if err else "·"
                    out_lines.append(f"{color}   {tag} {short(txt, 150)}{RESET}")
                else:
                    out_lines.append(f"{MAGENTA}▌{role}{RESET} {short(txt, 180)}")

    if not out_lines:
        return None
    return f"{DIM}{ts}{RESET} " + "\n".join(out_lines)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    replay = "--replay" in sys.argv
    path = args[0] if args else newest_session()
    if not path or not os.path.exists(path):
        print("Sessão não encontrada. Caminho:", path)
        sys.exit(1)
    print(f"{BOLD}▶ seguindo: {RESET}{os.path.basename(path)}")
    print(f"{DIM}  Ctrl+C para sair | --replay mostra o histórico existente{RESET}\n")

    pos = 0 if replay else os.path.getsize(path)
    seen = set()
    while True:
        try:
            with open(path) as f:
                f.seek(pos)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    key = (e.get("timestamp"), str(e)[:60])
                    if key in seen:
                        continue
                    seen.add(key)
                    rendered = render(e)
                    if rendered:
                        print(rendered, flush=True)
                pos = f.tell()
            time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nbye")
            break
        except Exception as ex:
            print(f"{RED}erro: {ex}{RESET}", file=sys.stderr)
            time.sleep(2)


if __name__ == "__main__":
    main()

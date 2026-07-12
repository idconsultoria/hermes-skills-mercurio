# Pi Session Retake Pattern (Delfos F4f, Jul 2026)

## Situation
GLM 5.2 via opencode-go started a timeline redesign task but appeared stalled:
- 33 entries in 6 minutes (all reads, no writes)
- Last entry: truncated thinking text "Let me think about t..."
- Process alive but 0% CPU for 4+ minutes
- No new entries in session JSONL

## Mistake Made
The agent killed the process (SIGKILL) assuming stall. In reality, GLM 5.2 on Fireworks backend was in a legitimate long thinking phase - extremely slow but still progressing. The model later produced 933 lines of timeline.js + CSS edits when given a chance.

## Correct Retake Procedure

```bash
# 1. Find the stalled session
ls -lt ~/.pi/agent/sessions/--*/*.jsonl

# 2. Verify it has real progress (not just error entries)
python3 -c "
import json
with open('session.jsonl') as f:
    entries = [json.loads(l) for l in f if l.strip()]
print(f'{len(entries)} entries')
last = entries[-1]
# Check if last entry has writes or is just thinking
for c in last.get('message',{}).get('content',[]):
    if isinstance(c,dict) and c.get('type')=='toolCall':
        print(f'Last tool: {c.get(\"name\")}')
"

# 3. Retake with short continuation prompt (NOT the full original prompt)
pi --session /path/to/session.jsonl \
  -p "Continue from where you stopped. STOP planning and START writing code now. Execute bash and write tools immediately." \
  --provider opencode-go --model glm-5.2 \
  --name "task-retake"

# 4. Monitor entries growing (NOT CPU or wall clock)
watch -n 30 'python3 -c "import json; e=[json.loads(l) for l in open(\"session.jsonl\") if l.strip()]; print(f\"Entries: {len(e)}\"); [print(c.get(\"name\",\"\")) for c in e[-1].get(\"message\",{}).get(\"content\",[]) if isinstance(c,dict) and c.get(\"type\")==\"toolCall\"]"'
```

## Key Lessons
- **Don't kill Pi based on CPU% or wall clock.** GLM 5.2 can take 6-12 minutes in thinking phase.
- **Check JSONL entry growth, not process activity.** If entries keep growing, Pi is working.
- **Only kill if entries haven't grown for >120s AND last toolCall wasn't a pending write.
- **Prompt matters for retake.** A short, direct "STOP planning, START writing" works better than re-explaining the task.
- **Cost already sunk.** Killing discards $0.05-0.10+ of reading context. Retaking reuses it.

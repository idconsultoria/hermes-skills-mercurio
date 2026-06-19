# Drive Batch Download — Pattern for Process Folders

Pattern used to batch-download 203 files (29 process folders × 4 setores) from a Google Drive structure into a local project directory. Reusable for any project that needs to pull structured data from Drive.

## Prerequisites

```bash
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
```

## Pattern: List → Map → Download by Setor

### Step 1: List all folders in parent

```bash
$GAPI drive search "'<PARENT_FOLDER_ID>' in parents" --raw-query --max 50
```

Output: JSON array with `id`, `name`, `mimeType` for each child.

### Step 2: Build a mapping file

Save `PREFIX|NAME|ID` to a text file for batch processing:

```bash
$GAPI drive search "'<PARENT>' in parents" --raw-query --max 50 | \
  python3 -c "import sys,json; [print(f['name'].split('-')[0]+'|'+f['name']+'|'+f['id']) for f in json.load(sys.stdin)]" \
  > /tmp/ids.txt
```

### Step 3: Download per process

For each process folder, list its subfolders, then download only specific types:

```bash
while IFS='|' read -r PREFIX NAME ID; do
    DIR="$BASE/$SETOR/$NAME"
    mkdir -p "$DIR"
    
    # List subfolders
    $GAPI drive search "'$ID' in parents" --raw-query --max 10 | \
      python3 -c "import sys,json; [print(f['id']+'|'+f['name']+'|'+f.get('mimeType','')) for f in json.load(sys.stdin)]" | \
      while IFS='|' read -r SID SNAME SMIME; do
        case "$SNAME" in
            *"POPs"*|*"Transcri"*|*"Question"*)
                # Google Docs → download as plain text
                $GAPI drive search "'$SID' in parents" --raw-query --max 10 | \
                  python3 -c "import sys,json; [print(f['id'],f['name']) for f in json.load(sys.stdin)]" | \
                  while read FID FNAME; do
                    O="$DIR/$FNAME"; [ -f "$O" ] && continue
                    $GAPI drive download "$FID" --export-mime text/plain --output "$O"
                done
                ;;
            *"XMLs"*)
                # Only images, skip .bpmn/.xml
                $GAPI drive search "'$SID' in parents" --raw-query --max 10 | \
                  python3 -c "import sys,json; [print(f['id'],f['name']) for f in json.load(sys.stdin) if 'image' in f.get('mimeType','') or f['name'].lower().endswith('.png')]" | \
                  while read FID FNAME; do
                    O="$DIR/$FNAME"; [ -f "$O" ] && continue
                    $GAPI drive download "$FID" --output "$O"
                done
                ;;
        esac
    done
done < /tmp/ids.txt
```

## Critical Pitfalls

### ⚠️ Drive IDs are CASE-SENSITIVE
Google Drive folder IDs contain mixed case (e.g., `19XwCorBD3fCmUoQeANKq_ecfnSS9WzIG`). Copy-pasting from terminal output can change case. Always verify:
```bash
$GAPI drive get <ID> 2>&1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','NOT FOUND'))"
```

### ⚠️ Google Docs export requires --export-mime
Downloading a Google Doc without `--export-mime text/plain` downloads nothing useful. Always use the flag for Docs, Sheets, and Slides.

### ⚠️ Shell subshell variable scoping
When piping to `while read`, the loop runs in a subshell. Variables set inside the loop are lost. For simple download scripts, use `[ -f "$O" ] && continue` to skip existing files rather than tracking state.

### ⚠️ Rate limiting
Google Drive API has quotas. For >100 files, process in batches with sleep between setores. Processing 29 folders with ~8 files each takes ~2-3 minutes.

### ⚠️ Parallel downloads
4 background processes (one per setor) work well with Drive API. Avoid more than 4 concurrent downloaders — the API rate-limits aggressively beyond that.

## Verification

After download:
```bash
# Count files per setor
for setor in setor-*/; do echo "$setor: $(find "$setor" -type f | wc -l) files"; done
# Verify specific file types
for setor in setor-*/; do echo "$setor: $(find "$setor" -name '*ranscri*' | wc -l) transcripts"; done
```

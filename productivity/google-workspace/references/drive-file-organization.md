# Drive File Organization

Moving files to folders and deduplicating after batch uploads.

## Problem

When batch-processing scripts (e.g. `kindle_volume_processor.py`) upload files, they upload to Drive root by default (`parents: ['root']`). After all files are uploaded, you need to:

1. Move them into the correct folder
2. Delete any duplicate copies (from overlapping batches or re-runs)

## Solution: `scripts/drive-move-to-folder.py`

Move all files matching a name pattern into a folder, then deduplicate:

```bash
# Move all Monster_Vol13_Q85 files into the Monster folder
python3 /opt/data/skills/productivity/google-workspace/scripts/drive-move-to-folder.py \
    "1lGbMpWC7PvP7FOQtgqV8c4nkgjDuNOrD" \
    "Monster_Vol13_Q85"
```

The script:
- Searches Drive for files whose `name contains` the pattern
- Moves matching files from current parents → target folder
- If multiple copies exist, keeps one (prefers the one already in folder), deletes the rest

### Batch loop pattern

After a series is fully uploaded, loop through all volumes:

```bash
FOLDER_ID="1lGbMpWC7PvP7FOQtgqV8c4nkgjDuNOrD"
for v in $(seq 1 18); do
  python3 /opt/data/skills/productivity/google-workspace/scripts/drive-move-to-folder.py \
    "$FOLDER_ID" \
    "Monster_Vol$(printf '%02d' $v)_Q85"
done
```

### When to use

- After any batch upload sequence where files were uploaded to root
- When the same batch was dispatched twice and you need to deduplicate
- When old files with different naming conventions exist alongside new ones

### Limitations

- The script uses `name contains` (case-insensitive substring match) — may match unintended files if the pattern is too broad
- File search is paginated at 20 results — if more than 20 files match the same pattern, the script misses the overflow. For large sets (>20 duplicates), use the API directly with pagination
- Google Drive API's `parents` field may be `null` for shared drive files — the script handles this by treating `None` as "not in folder"

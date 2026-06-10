# Google Docs API — Inline Update / Replace via batchUpdate

The `google_api.py` script only supports `docs get`, `docs create`, and `docs append`.
For **inline replacements** (finding a block of text and replacing it mid-document),
you must call the Google Docs REST API `batchUpdate` endpoint directly.

## When to use

- You need to **replace a specific paragraph or section** in the middle of a document
- You need **deleteContentRange** + **insertText** as a single atomic operation
- The `docs append` command is insufficient because you need to modify existing content

## How it works

```python
import json, urllib.request

DOC_ID = "your-doc-id"

# Load the OAuth token
with open("/opt/data/google_token.json") as f:
    token_data = json.load(f)

access_token = token_data.get("access_token") or token_data.get("token")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# Step 1: GET document to find start/end indices of content to replace
url = f"https://docs.googleapis.com/v1/documents/{DOC_ID}"
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
doc_json = json.loads(resp.read())

content = doc_json["body"]["content"]

# Step 2: Scan paragraphs to find the text boundaries
start_idx = end_idx = None
for elem in content:
    if "paragraph" in elem:
        text = ""
        for pe in elem["paragraph"]["elements"]:
            if "textRun" in pe:
                text += pe["textRun"]["content"]
        if "START_MARKER" in text and start_idx is None:
            start_idx = elem["startIndex"]
        if "END_MARKER" in text and start_idx is not None and end_idx is None:
            end_idx = elem["startIndex"]

# Step 3: Build batch update — delete old, insert new
new_text = "Your replacement content here\n"

batch = {
    "requests": [
        {"deleteContentRange": {"range": {"startIndex": start_idx, "endIndex": end_idx}}},
        {"insertText": {"location": {"index": start_idx}, "text": new_text}},
    ]
}

batch_url = f"https://docs.googleapis.com/v1/documents/{DOC_ID}:batchUpdate"
batch_data = json.dumps(batch).encode()
req = urllib.request.Request(batch_url, data=batch_data, headers=headers, method="POST")
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
```

## Index gotchas

- **`startIndex` is inclusive**, `endIndex` is **exclusive** — like Python slicing
- Paragraphs include their trailing `\n` in the index range
- Indexes are byte-based for Unicode, so multi-byte characters count as 1
- When using `deleteContentRange`, be careful not to delete structural elements (table boundaries, section breaks) unless intended
- The `endIndex` of the target block is usually the `startIndex` of the **next paragraph** in the `content` array

## Style bleeding (most common pitfall)

When you apply `updateTextStyle` with `bold=True` to a heading, the bold **bleeds into the next paragraph** if your range includes the trailing `\n` of the heading paragraph.

**Bad — bold bleeds into the paragraph below:**
```python
# Range covers "Title\n" — the \n propagates bold to the next paragraph
"updateTextStyle": {
    "range": {"startIndex": s, "endIndex": e},  # e = end of "Title\n"
    "textStyle": {"bold": True},
    "fields": "bold",
}
```

**Good — exclude the trailing newline from styled ranges:**
```python
title_text = elem["paragraph"]["elements"][0]["textRun"]["content"]
title_end = elem["startIndex"] + len(title_text.strip("\n"))

"updateTextStyle": {
    "range": {"startIndex": s, "endIndex": s + len(title_text.rstrip('\n'))},
    "textStyle": {"bold": True},
    "fields": "bold",
}
```

**Defensive — explicitly unbold everything after the styled range to prevent bleed-through:**
```python
# After applying bold to the title range [s, s+title_len), apply bold=False to the rest
"updateTextStyle": {
    "range": {
        "startIndex": s + title_len,       # right after title text
        "endIndex": rest_end,               # end of the section
    },
    "textStyle": {"bold": False},
    "fields": "bold",
}
```

**Why this happens:** Google Docs stores text styles on text runs. The `\n` at the end of a paragraph is its own text run or is part of the last run. When you bold a range covering `\n`, the style attaches to the paragraph break itself, which the rendering engine inherits for the next paragraph.

## Useful batch operations

| Operation | Use case |
|-----------|----------|
| `deleteContentRange` | Remove existing text block |
| `insertText` | Insert new text at a position |
| `updateParagraphStyle` | Change alignment, line spacing |
| `updateTextStyle` | Change font, bold, italic of a range |

## Limitations

- No regex-based find-and-replace — you must compute indices manually
- Each batch request is limited (practical limit: ~20 operations per batch)
- Cannot insert images via this method (use Drive API for that)

# Graph HTML Template

Placeholder template for the D3.js skills graph. The `__DATA_PLACEHOLDER__` token is replaced at generation time with the full nodes+edges JSON.

## Usage
```bash
cd /opt/data/skills
python3 scripts/generate_graph.py
```

## Features
- Force-directed layout with zoom/pan
- Similar edges: dashed gray
- Uses/used_by edges: solid blue with arrow
- Nodes colored by category (14 colors)
- Node size proportional to SKILL.md file size
- Click modal: summary + description + relations
- Hover: highlight connected subgraph
- Text filter with dimming
- Mobile responsive with resize handler
- Parent→child and uses→used_by edges deduplicated (one edge per pair)

## Template location
`/opt/data/skills/skills_graph_template.html`

## Output
`/opt/data/skills/skills_graph.html`

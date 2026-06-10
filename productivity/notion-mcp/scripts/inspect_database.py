#!/usr/bin/env python3
"""
Inspect a Notion database schema and its records via the Notion MCP server.

Usage:
  /opt/hermes/.venv/bin/python3 scripts/inspect_database.py <data_source_id>

Outputs:
  - Full property schema with types, options, status groups
  - Relation targets and rollup sources
  - Sample records showing actual field values

Requires:
  - mcp Python package in Hermes venv
  - Valid OAuth tokens at $HERMES_HOME/mcp-tokens/notion.json
"""

import asyncio, json, re, sys, os
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

HERMES_HOME = os.environ.get('HERMES_HOME', '/opt/data')
TOKEN_PATH = os.path.join(HERMES_HOME, 'mcp-tokens', 'notion.json')
MCP_URL = 'https://mcp.notion.com/mcp'


async def fetch(session, tool, params):
    result = await session.call_tool(tool, params)
    return json.loads(result.content[0].text)


def print_schema(schema):
    """Print formatted property schema."""
    for prop_name, prop in schema.items():
        ptype = prop.get('type', '?')
        opt_list = prop.get('options', [])
        opt_str = f' [{", ".join(o["name"] for o in opt_list)}]' if opt_list else ''

        extra = ''
        if ptype == 'relation':
            extra = f' → relation to: {prop.get("dataSourceUrl","")[:60]}...'
        elif ptype == 'rollup':
            agg = prop.get('aggregation', {})
            extra = f' → rollup ({agg.get("operator","?")}) of: {agg.get("groupName","?")}'
        elif ptype == 'status':
            groups = prop.get('groups', {})
            parts = []
            for gname, opts in groups.items():
                vals = ', '.join(o['name'] for o in opts)
                parts.append(f'{gname}=[{vals}]')
            extra = ' | ' + ' | '.join(parts)

        pname = prop_name or '(title)'
        print(f'  {pname}: {ptype}{opt_str}{extra}')


def print_record(record, schema):
    """Print a record showing field values."""
    props = record.get('properties', {})
    title = record.get('title', '') or record.get('id', '?')[:20]

    # Find the title property name
    title_prop = ''
    for pname, p in schema.items():
        if p.get('type') == 'title':
            title_prop = pname
            break

    # Try to extract title from properties
    if title_prop and props.get(title_prop):
        title_parts = props[title_prop].get('title', [])
        title = ''.join(t.get('text', {}).get('content', '') for t in title_parts)

    print(f'\n  📄 {title}')

    for pname, pvalue in props.items():
        if pname == title_prop:
            continue
        ptype = pvalue.get('type', '')

        type_handlers = {
            'status': lambda v: v.get('status', {}).get('name', '-'),
            'select': lambda v: v.get('select', {}).get('name', '-'),
            'multi_select': lambda v: ', '.join(o['name'] for o in v.get('multi_select', [])) or '-',
            'rich_text': lambda v: ''.join(t.get('text', {}).get('content', '') for t in v.get('rich_text', [])) or '-',
            'date': lambda v: (lambda d: f'{d.get("start","")} → {d.get("end","")}')(v.get('date', {})) if v.get('date') else '-',
            'number': lambda v: str(v.get('number', '-')),
            'checkbox': lambda v: '✅' if v.get('checkbox') else '⬜',
            'person': lambda v: ', '.join(u.get('name', '?') for u in v.get('people', [])) or '-',
            'relation': lambda v: f'{len(v.get("relation", []))} relations' if v.get('relation') else '-',
            'rollup': lambda v: str(v.get('rollup', {}).get('number', '-')),
            'url': lambda v: v.get('url', '-'),
            'formula': lambda v: str(v.get('formula', {}).get('string', v.get('formula', {}).get('number', '-'))),
            'created_time': lambda v: v.get('created_time', '-'),
            'last_edited_time': lambda v: v.get('last_edited_time', '-'),
        }

        handler = type_handlers.get(ptype)
        val = handler(pvalue) if handler else str(pvalue.get(ptype, '?'))[:50]
        print(f'    {pname}: {val}')


async def main():
    if len(sys.argv) < 2:
        print('Usage: inspect_database.py <data_source_id>')
        sys.exit(1)

    ds_id = sys.argv[1]

    with open(TOKEN_PATH) as f:
        tok = json.load(f)

    async with streamablehttp_client(
        url=MCP_URL,
        headers={'Authorization': f'Bearer {tok["access_token"]}'},
        timeout=30
    ) as streams:
        read, write, close_fn = streams
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Fetch the data source schema
            print(f'🔍 Inspecting data source: {ds_id}\n')
            result = await fetch(session, 'notion-fetch', {'id': ds_id})
            text = result.get('text', '')

            # Extract schema from data-source-state
            m = re.search(r'<data-source-state>(.*?)</data-source-state>', text, re.DOTALL)
            if not m:
                print('❌ No data-source-state found. Check the ID.')
                sys.exit(1)

            schema_json = json.loads(m.group(1))
            schema = schema_json.get('schema', {})

            print(f'📊 Database: {schema_json.get("name", "Untitled")}')
            print(f'   Icon: {schema_json.get("icon", "none")}')
            print(f'   Template: {schema_json.get("default_page_template", "none")}')
            print(f'\n📋 Properties ({len(schema)}):')
            print('─' * 60)
            print_schema(schema)

            # 2. Query records via broad search
            print(f'\n📝 Records in workspace (search broadly):')
            print('─' * 60)

            try:
                result2 = await fetch(session, 'notion-search', {
                    'query': 'a',
                    'page_size': 25,
                    'filters': {'type': 'page'}
                })

                records = result2.get('results', [])
                count = min(5, len(records))
                for i in range(count):
                    r = records[i]
                    title = r.get('title', '?')
                    print(f'  → {title[:60]} | {r.get("id","?")}')

                if not records:
                    print('  (no records found)')

                print(f'\n✅ Done. {len(records)} records found.')
            except Exception as e:
                print(f'\n❌ Error querying records: {e}')


if __name__ == '__main__':
    asyncio.run(main())

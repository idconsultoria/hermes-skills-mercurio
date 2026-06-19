# Template: Gerador de HTMLs de Análise Sistêmica
# 
# Este script é a referência canônica para gerar os HTMLs setoriais e global.
# Ele aplica TODOS os padrões: identidade ID Consultoria, setas direcionais,
# símbolos +/-, cores distinguíveis, descrições enriquecidas e markdown→HTML.
#
# ⚠️ REGRA CRÍTICA: Toda formatação de texto (negrito, código, itálico) deve
# ser gerada como tags HTML diretamente nas strings Python, NUNCA como raw
# markdown convertido via regex no HTML final. Regex no HTML final CORROMPE
# o JavaScript do D3.js.
#
# Uso: python3 generator-template.py
# Requer: Python 3.8+, acesso à internet (CDN de fontes e D3.js)

import json
from collections import defaultdict

# ============================================================
# CONFIGURAÇÃO DE DESIGN (ID Consultoria)
# ============================================================
COLORS = {
    "cultural": {"fill": "#C9A227", "stroke": "#E8C84A", "badge_bg": "rgba(201,162,39,0.12)", "label": "Cultural"},
    "tecnica": {"fill": "#66E8F1", "stroke": "#A5F3FC", "badge_bg": "rgba(102,232,241,0.12)", "label": "Técnica"},
    "organizacional": {"fill": "#6366F1", "stroke": "#A5B4FC", "badge_bg": "rgba(99,102,241,0.15)", "label": "Organizacional"},
}

FONTS_CDN = "Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700|Nunito+Sans:opsz,wght@6..12,400;6..12,600|IBM+Plex+Mono:wght@400;600"

# ============================================================
# FUNÇÕES DE GERAÇÃO DE TEXTO
# ============================================================

def build_node_description(node):
    """Constrói descrição de 2 parágrafos para o painel de clique.
    ⚠️ Usa tags HTML diretamente, não markdown."""
    cat = COLORS.get(node["cat"], {}).get("label", node["cat"])
    proc = node.get("processos", "Todos")
    p1 = node.get("desc", "")
    ev = node.get("evidencia", "")
    p2 = f"Natureza: {cat}. Processos afetados: {proc}."
    if ev:
        p2 += f"\n\nEvidência: \"{ev}\""
    return f"{p1}\n\n{p2}"

def build_cycle_analysis(cycles, nmap, adj):
    """Constrói análise de ciclos em HTML.
    ⚠️ Gera tags HTML diretamente (strong, code, em), NUNCA raw markdown."""
    parts = []
    for i, cycle in enumerate(cycles[:15]):
        labels = [nmap[nid]["label"] for nid in cycle]
        cats = [nmap[nid]["cat"] for nid in cycle]
        path_desc = " → ".join([nid for nid in cycle]) + " → " + cycle[0]
        has_dashed = any(nmap[nid]["id"].startswith("GAR") for nid in cycle)
        cycle_type = "vicioso" if not has_dashed else "misto (com mitigação parcial)"
        
        if len(cycle) == 2:
            a, b = cycle[0], cycle[1]
            mechanism = (
                f"Mecanismo: {a} — {labels[0]} — alimenta diretamente {b} — {labels[1]}. "
                f"Por sua vez, {b} retroalimenta {a}, fechando um ciclo de reforço mútuo. "
                f"Quanto mais intenso um dos fatores, mais o outro se agrava."
            )
            consequence = (
                f"Consequência: Ciclo do tipo {cycle_type}. "
                f"A organização está presa em uma dinâmica onde {a} e {b} se perpetuam. "
                f"Para quebrá-lo, intervir em ao menos um dos dois nós."
            )
        elif len(cycle) == 3:
            a, b, c = cycle[0], cycle[1], cycle[2]
            mechanism = (
                f"Mecanismo: {a} — {labels[0]} — desencadeia {b} — {labels[1]} — "
                f"que produz {c} — {labels[2]} —, e este realimenta {a}. "
                f"A latência entre causa e efeito mascara a origem do problema."
            )
            consequence = (
                f"Consequência: Ciclo do tipo {cycle_type} com 3 estágios. "
                f"Intervenções apenas no sintoma final ({c}) não quebram o ciclo."
            )
        else:
            mechanism = (
                f"Mecanismo: Ciclo de {len(cycle)} estágios onde múltiplos fatores se encadeiam: " + 
                " → ".join([labels[j] for j in range(len(cycle))]) + ". "
                f"Com {len(cycle)} nós interligados, a dinâmica é difícil de perceber no dia a dia."
            )
            central = max(cycle, key=lambda nid: len(adj.get(nid, [])))
            consequence = (
                f"Consequência: Dada a complexidade ({len(cycle)} estágios, tipo {cycle_type}), "
                f"priorizar {central} — {nmap[central]['label']} — que é o nó com maior centralidade."
            )
        
        name = f"Ciclo: {' ↔ '.join(labels[:2])}" if len(cycle) <= 3 else f"Ciclo {i+1}: {labels[0]}"
        # ⚠️ HTML tags usadas diretamente — nunca raw ** ou `
        parts.append(
            f'<div class="cycle">'
            f'<h3>{name}</h3>'
            f'<p class="cycle-path">{path_desc}</p>'
            f'<p><strong>Mecanismo:</strong> {mechanism}</p>'
            f'<p><strong>Consequência:</strong> {consequence}</p>'
            f'</div>'
        )
    return "".join(parts)

# ============================================================
# DETECÇÃO DE CICLOS
# ============================================================

def detect_cycles(nodes, links, max_depth=5):
    adj = defaultdict(list)
    for l in links:
        adj[l["source"]].append(l["target"])
    nmap = {n["id"]: n for n in nodes}
    cycles, seen = [], set()
    
    def dfs(start, curr, path, depth):
        if depth > max_depth:
            return
        for nxt in adj[curr]:
            if nxt == start and depth >= 2:
                c = tuple(sorted(path))
                if c not in seen:
                    seen.add(c)
                    cycles.append(path + [nxt])
            elif nxt not in path and nxt != start:
                dfs(start, nxt, path + [nxt], depth + 1)
    
    for nid in nmap:
        dfs(nid, nid, [nid], 1)
    cycles.sort(key=len)
    
    cc = defaultdict(int)
    for c in cycles:
        for n in c:
            cc[n] += 1
    
    return cycles, cc, nmap, adj

# ============================================================
# GERAÇÃO DO HTML
# ============================================================

def generate_html(setor_nome, processos_desc, nodes, links, outpath, is_global=False):
    """Gera um HTML de análise sistêmica completo.
    
    Args:
        setor_nome: Nome do setor (ex: 'ASP') ou 'Sergipetec' para global
        processos_desc: Descrição dos processos
        nodes: Lista de nós [{id, cat, label, desc, processos, evidencia?}]
        links: Lista de arestas [{source, target, dashed?}]
        outpath: Caminho de saída do arquivo .html
        is_global: Se True, gera o HTML cross-setor
    """
    # Enriquecer descrições dos nós
    for n in nodes:
        n["desc_rich"] = build_node_description(n)
    
    # Detectar ciclos
    cycles, cc, nmap, adj = detect_cycles(nodes, links)
    cycle_html = build_cycle_analysis(cycles, nmap, adj)
    
    # Ranking de alavancas
    ranked_rows = []
    for nid, cnt in sorted(cc.items(), key=lambda x: -x[1])[:20]:
        n = nmap[nid]
        cat_label = COLORS.get(n["cat"], {}).get("label", n["cat"])
        ranked_rows.append(
            f'<tr><td class="mono">{nid}</td>'
            f'<td>{n["label"]}</td>'
            f'<td><span class="badge {n["cat"]}">{cat_label}</span></td>'
            f'<td class="num">{cnt}</td></tr>'
        )
    
    title = f"Análise Sistêmica {'Global' if is_global else '— Setor ' + setor_nome}"
    h1_icon = "🌐" if is_global else "🔬"
    
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    links_json = json.dumps(links, ensure_ascii=False)
    
    # ⚠️ Template HTML com TODOS os padrões aplicados:
    # - ID Consultoria colors (gold #C9A227, teal #66E8F1, indigo #6366F1)
    # - ID fonts (Bricolage Grotesque, Nunito Sans, IBM Plex Mono)
    # - Setas direcionais em TODAS as arestas (solid e dashed)
    # - Labels +/- a 78% da aresta (próximo à ponta da seta)
    # - Linhas tracejadas visíveis (opacity 0.55, width 1.5)
    # - Ciclos com <strong>, <code>, <em> (HTML, não markdown)
    # - Painel de clique com descrição de 2 parágrafos
    
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — Sergipetec</title>
<link href="https://fonts.googleapis.com/css2?family={FONTS_CDN}&display=swap" rel="stylesheet">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
:root{{--bg:#050A0F;--bg-card:#0B1320;--bg-card-hover:#122035;--line:#1B2A3F;--text:#E6EDF3;--text-muted:#8B98A8;--accent:#66E8F1;--gold:#C9A227;--indigo:#6366F1;--font-headline:'Bricolage Grotesque',sans-serif;--font-body:'Nunito Sans',sans-serif;--font-mono:'IBM Plex Mono',monospace}}
*{{margin:0;box-sizing:border-box}}
body{{background:var(--bg);color:var(--text);font-family:var(--font-body);line-height:1.7;-webkit-font-smoothing:antialiased}}
h1{{font-family:var(--font-headline);font-size:clamp(22px,4vw,32px);font-weight:700;letter-spacing:-0.5px;margin-bottom:6px}}
h2{{font-family:var(--font-headline);font-size:clamp(17px,2.5vw,22px);font-weight:600;margin:40px 0 14px;padding-bottom:10px;border-bottom:1px solid var(--line)}}
h3{{font-family:var(--font-headline);font-size:15px;font-weight:600;margin:20px 0 6px;color:var(--accent)}}
p{{color:var(--text-muted);margin:8px 0;max-width:72ch}}
nav{{position:fixed;top:0;left:0;right:0;z-index:200;background:rgba(5,10,15,0.88);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--line);padding:10px 20px;display:flex;gap:20px;align-items:center;flex-wrap:wrap}}
nav a{{color:var(--text-muted);text-decoration:none;font-size:12px;font-weight:600;letter-spacing:0.3px;text-transform:uppercase;transition:color .15s}}
nav a:hover{{color:var(--accent)}}
nav .brand{{font-weight:700;color:var(--text);font-size:13px;margin-right:auto;font-family:var(--font-headline)}}
.container{{max-width:1100px;margin:0 auto;padding:70px 20px 40px}}
#diagram-container{{position:relative;width:100%;height:80vh;min-height:500px;background:var(--bg-card);border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:20px 0}}
#diagram-container svg{{width:100%;height:100%;display:block}}
.legend{{position:absolute;bottom:14px;left:14px;background:rgba(11,19,32,0.92);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:11px;z-index:20;backdrop-filter:blur(8px)}}
.legend .row{{display:flex;align-items:center;gap:7px;margin:3px 0;color:var(--text-muted)}}
.legend .dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
#panel{{position:absolute;top:14px;right:14px;width:350px;max-height:65vh;overflow-y:auto;background:rgba(11,19,32,0.96);border:1px solid var(--line);border-radius:12px;padding:18px;z-index:20;backdrop-filter:blur(8px);display:none;box-shadow:0 8px 32px rgba(0,0,0,0.4)}}
#panel .ph{{font-size:14px;font-weight:600;margin-bottom:4px;color:var(--text)}}
#panel .pid{{font-size:10px;color:var(--text-muted);margin-bottom:8px;font-family:var(--font-mono)}}
#panel .badge{{display:inline-block;font-size:9px;padding:3px 8px;border-radius:4px;margin-bottom:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.4px}}
#panel .badge.cultural{{background:rgba(201,162,39,0.15);color:#C9A227}}
#panel .badge.tecnica{{background:rgba(102,232,241,0.15);color:#66E8F1}}
#panel .badge.organizacional{{background:rgba(99,102,241,0.18);color:#A5B4FC}}
#panel .pdesc{{font-size:12px;line-height:1.75;color:var(--text-muted);white-space:pre-line}}
#panel .close{{position:absolute;top:10px;right:10px;cursor:pointer;color:var(--text-muted);font-size:15px;line-height:1}}
#panel .close:hover{{color:var(--text)}}
.link{{stroke:#4A5A75;stroke-opacity:0.55;fill:none}}
.link.dashed{{stroke-dasharray:6,4;stroke-opacity:0.55}}
.edge-label rect{{fill:rgba(11,19,32,0.85);rx:4}}
.edge-label text{{font-family:var(--font-mono);font-size:10px;fill:var(--text-muted);text-anchor:middle;dominant-baseline:central;font-weight:600}}
.node circle{{stroke-width:2.5px;cursor:pointer;transition:r .12s,stroke-width .12s}}
.node circle.cultural{{fill:#C9A227;stroke:#E8C84A}}
.node circle.tecnica{{fill:#66E8F1;stroke:#A5F3FC}}
.node circle.organizacional{{fill:#6366F1;stroke:#A5B4FC}}
.node text.id{{font-family:var(--font-mono);font-size:8.5px;fill:var(--text-muted);text-anchor:middle;font-weight:600}}
.node text.label{{font-family:var(--font-body);font-size:9.5px;fill:var(--text);text-anchor:middle}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:13px}}
th{{text-align:left;padding:10px 14px;border-bottom:2px solid var(--line);color:var(--text-muted);font-weight:500;font-size:10px;text-transform:uppercase;letter-spacing:0.6px;font-family:var(--font-headline)}}
td{{padding:10px 14px;border-bottom:1px solid rgba(27,42,63,0.5);color:var(--text-muted)}}
td.mono{{font-family:var(--font-mono);font-size:11px;color:var(--text)}}
td.num{{font-family:var(--font-mono);font-weight:600;color:var(--accent)}}
tr:hover td{{background:var(--bg-card-hover)}}
.badge{{display:inline-block;font-size:9px;padding:2px 7px;border-radius:3px;font-weight:600}}
.badge.cultural{{background:rgba(201,162,39,0.12);color:#C9A227}}
.badge.tecnica{{background:rgba(102,232,241,0.12);color:#66E8F1}}
.badge.organizacional{{background:rgba(99,102,241,0.15);color:#A5B4FC}}
.cycle{{background:var(--bg-card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:14px 0}}
.cycle h3{{margin-top:0;font-size:14px}}
.cycle p{{margin:8px 0;line-height:1.7}}
.cycle-path{{font-family:var(--font-mono);font-size:11px;color:var(--accent);word-break:break-all;margin-bottom:10px!important}}
@media(max-width:768px){{.container{{padding:56px 10px 24px}}#diagram-container{{height:55vh;min-height:380px;border-radius:0}}#panel{{width:260px;right:4px;top:8px;max-height:55vh;padding:14px}}nav{{padding:8px 12px;gap:12px}}nav a{{font-size:10px}}}}
</style>
</head>
<body>
<nav><span class="brand">Sergipetec · Análise Sistêmica</span><a href="#diagrama">Diagrama</a><a href="#ciclos">Ciclos</a><a href="#ranking">Alavancas</a></nav>
<div class="container">
<h1>{h1_icon} {title} — Sergipetec</h1>
<p>{processos_desc} · <span class="badge cultural">Cultural</span> <span class="badge tecnica">Técnica</span> <span class="badge organizacional">Organizacional</span></p>
<h2 id="diagrama">Diagrama de Loop Causal</h2>
<p>Clique nos nós para ver detalhes. Arraste para reorganizar. <strong>+</strong> = reforço, <strong>−</strong> = balanceamento. Setas indicam direção da relação causal.</p>
<div id="diagram-container">
<div class="legend"><div class="row"><span class="dot" style="background:#C9A227"></span> Cultural</div><div class="row"><span class="dot" style="background:#66E8F1"></span> Técnica</div><div class="row"><span class="dot" style="background:#6366F1"></span> Organizacional</div><div class="row" style="margin-top:6px;font-size:10px">+ reforço / − balanceamento</div></div>
<div id="panel"><span class="close" onclick="this.parentElement.style.display='none'">✕</span><div class="ph" id="p-title"></div><div class="pid" id="p-id"></div><span class="badge" id="p-cat"></span><div class="pdesc" id="p-desc"></div></div>
<svg id="canvas"></svg></div>
<script>
const nodes={nodes_json};
const links={links_json};
const catLabels={{cultural:'Cultural',tecnica:'Técnica',organizacional:'Organizacional'}};
const svg=d3.select("#canvas"),c=document.getElementById("diagram-container"),w=c.clientWidth,h=c.clientHeight;
svg.append("defs").append("marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",19).attr("refY",0).attr("markerWidth",8).attr("markerHeight",8).attr("orient","auto").append("path").attr("d","M0,-4L8,0L0,4").attr("fill","#8B98A8");
const g=svg.append("g");
svg.call(d3.zoom().scaleExtent([0.25,3]).on("zoom",e=>g.attr("transform",e.transform)));
const sim=d3.forceSimulation(nodes).force("link",d3.forceLink(links).id(d=>d.id).distance(130).strength(0.25)).force("charge",d3.forceManyBody().strength(-280)).force("center",d3.forceCenter(w/2,h/2)).force("collide",d3.forceCollide().radius(38));
const linkG=g.append("g").selectAll("g").data(links).join("g");
linkG.append("line").attr("class",d=>"link"+(d.dashed?" dashed":"")).attr("stroke-width",d=>d.dashed?1.5:1.8).attr("marker-end","url(#arrow)");
const edgeLabel=linkG.append("g").attr("class","edge-label");
edgeLabel.append("rect").attr("width",18).attr("height",16).attr("x",-9).attr("y",-8);
edgeLabel.append("text").text(d=>d.dashed?"−":"+");
const nodeG=g.append("g").selectAll("g").data(nodes).join("g").attr("class","node").call(d3.drag().on("start",(e,d)=>{{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}}).on("drag",(e,d)=>{{d.fx=e.x;d.fy=e.y;}}).on("end",(e,d)=>{{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}})).on("click",(e,d)=>showPanel(d));
nodeG.append("circle").attr("r",17).attr("class",d=>d.cat);
nodeG.append("text").attr("class","id").attr("dy",-22).text(d=>d.id);
nodeG.append("text").attr("class","label").attr("dy",4).each(function(d){{const w=d.label.split(" ");let lines=[],cur="";for(const x of w){{if((cur+" "+x).length>18){{lines.push(cur);cur=x}}else cur=cur?cur+" "+x:x}}if(cur)lines.push(cur);for(let i=0;i<Math.min(lines.length,2);i++)d3.select(this).append("tspan").attr("x",0).attr("dy",i===0?0:10).text(lines[i]);}});
sim.on("tick",()=>{{linkG.selectAll("line").attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);edgeLabel.attr("transform",d=>`translate(${{d.source.x*0.22+d.target.x*0.78}},${{d.source.y*0.22+d.target.y*0.78}})`);nodeG.attr("transform",d=>`translate(${{d.x}},${{d.y}})`);}});
function showPanel(d){{const p=document.getElementById("panel");p.style.display="block";document.getElementById("p-title").textContent=d.label;document.getElementById("p-id").textContent=d.id;const cat=document.getElementById("p-cat");cat.className="badge "+d.cat;cat.textContent=catLabels[d.cat]||d.cat;document.getElementById("p-desc").textContent=d.desc_rich||d.desc||"";}}
window.addEventListener("resize",()=>{{const c=document.getElementById("diagram-container");svg.attr("viewBox",`0 0 ${{c.clientWidth}} ${{c.clientHeight}}`);}});
</script>
<h2 id="ciclos">Análise de Ciclos</h2>
<p>Foram detectados <strong>{len(cycles)} ciclos</strong>. Cada ciclo é analisado abaixo com seu mecanismo causal e consequência.</p>
{cycle_html if cycle_html else "<p>Nenhum ciclo detectado.</p>"}
<h2 id="ranking">Nós-Alavanca (por participação em ciclos)</h2>
<p>Quanto mais ciclos um nó participa, maior o impacto sistêmico de resolvê-lo.</p>
<table><thead><tr><th>Nó</th><th>Descrição</th><th>Natureza</th><th>Ciclos</th></tr></thead><tbody>
{"".join(ranked_rows) if ranked_rows else "<tr><td colspan='4'>Nenhum nó em ciclos.</td></tr>"}
</tbody></table>
<p style="margin-top:24px;font-size:10px;color:var(--text-muted);opacity:0.6">Gerado pelo Pipeline de Aumentação de Processos · ID Consultoria · Etapa 1</p>
</div></body></html>'''
    
    with open(outpath, 'w') as f:
        f.write(html)
    
    return len(nodes), len(links), len(cycles)


# ============================================================
# EXEMPLO DE USO
# ============================================================
if __name__ == "__main__":
    # Este é um exemplo mínimo. Substitua pelos dados reais do projeto.
    demo_nodes = [
        {"id": "DOR-EX-01", "cat": "organizacional", "label": "Exemplo de dor",
         "desc": "Descrição da dor com contexto e impacto.", "processos": "EX-001"},
    ]
    demo_links = []
    n, e, c = generate_html("Exemplo", "1 processo. 1 dor.", demo_nodes, demo_links, "/tmp/demo.html")
    print(f"Demo gerado: {n} nós, {e} arestas, {c} ciclos")

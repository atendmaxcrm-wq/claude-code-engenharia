#!/usr/bin/env python3
# Baixa o DESIGN.md de um estilo do Refero Styles (styles.refero.design: design systems de sites REAIS, feitos para agentes:
# cores com papel, tipografia com substituto do Google Fonts, espacamento, raios, sombras, CSS pronto).
# Dica do Felipe Borges (video 7EDd1ND1cY4, passo 4 "inspiracao"). Entra na Fase 1 como referencia destilada.
# uso: refero.py <url-do-estilo> [saida.md]        lista de estilos: https://styles.refero.design/
import html, re, sys, urllib.request
url = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "DESIGN-referencia.md"
pg = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8")
m = re.search(r'<pre[^>]*><code[^>]*>(# .+?)</code></pre>', pg, re.S)
if not m: sys.exit("nao achei o DESIGN.md na pagina (layout do Refero mudou?)")
md = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
open(out, "w", encoding="utf-8").write(f"<!-- fonte: {url} -->\n{md}\n")
print(f"{out}: {len(md)} caracteres, {md.count(chr(10) + '## ')} secoes | {md.splitlines()[0]}")

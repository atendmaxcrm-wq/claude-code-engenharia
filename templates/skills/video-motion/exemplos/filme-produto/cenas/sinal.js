(c, i, x) => {
  // tres palavras empilhadas, uma por batida par, com mascara; a ultima na cor; uma linha cruza na batida 6
  const { tl, el, esc, box, W, H, B, cor, mola, tremida } = x, T = c.tBatidas;
  const ps = ["Sinal.", "Forma.", "Agente."], tam = Math.round(Math.min(W, H) * .2);
  const y0 = H / 2 - tam * 1.6;
  ps.forEach((p, k) => {
    const d = el(`<div style="position:absolute;left:0;right:0;top:${y0 + k * tam * 1.05}px;text-align:center;overflow:hidden;font-weight:700;font-size:${tam}px;letter-spacing:-.05em;line-height:1.05"><span style="display:inline-block;color:${k === 2 ? cor : "inherit"}">${esc(p)}</span></div>`, box);
    tl.from(d.firstChild, { yPercent: 110, duration: .6, ease: mola() }, T[k * 2]);
    if (k < 2) tl.to(d, { opacity: .28, duration: .4 }, T[k * 2 + 2]);
  });
  const ln = el(`<div style="position:absolute;left:${W * .12}px;width:${W * .76}px;top:${y0 + tam * 3.35}px;height:6px;background:${cor};transform-origin:left center"></div>`, box);
  tl.from(ln, { scaleX: 0, duration: B * 1.5, ease: "power3.inOut" }, T[6]);
  tremida(T[6], .8);
}

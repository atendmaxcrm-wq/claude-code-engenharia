#!/usr/bin/env python3
# python3 captura.py revisao r1  -> 1 quadro a cada 0,5 s + folha | python3 captura.py tudo -> quadros 30 fps + MP4 com som
import os, subprocess, sys, time
from multiprocessing import Process
AQUI=os.path.dirname(os.path.abspath(__file__)); FPS=30; TOTAL=64.0; W,H=1080,1920
def trab(ts,pasta,nomes):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav=p.chromium.launch(args=["--disable-gpu","--force-color-profile=srgb","--allow-file-access-from-files"])
        pg=nav.new_page(viewport={"width":W,"height":H},device_scale_factor=1)
        pg.on("pageerror",lambda e:print("ERRO NA PAGINA:",e))
        pg.goto("file://"+os.path.join(AQUI,"filme.html")); pg.wait_for_function("!!window.PRONTO",timeout=30000)
        c=pg.locator("#palco")
        for t,n in zip(ts,nomes):
            pg.evaluate(f"window.render({t:.5f})"); c.screenshot(path=os.path.join(pasta,n),type="jpeg",quality=92)
        nav.close()
def cap(ts,pasta,nomes,n=4):
    os.makedirs(pasta,exist_ok=True); ps=[Process(target=trab,args=(ts[i::n],pasta,nomes[i::n])) for i in range(n)]
    [p.start() for p in ps]; [p.join() for p in ps]
    if any(p.exitcode for p in ps): raise SystemExit("captura falhou")
def ff(a): subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y"]+a,check=True)
if __name__=="__main__":
    modo=sys.argv[1]; t0=time.time()
    if modo=="revisao":
        r=sys.argv[2]; pasta=os.path.join(AQUI,"out","revisao",r); ts=[i*.5+.25 for i in range(int(TOTAL*2))]
        cap(ts,pasta,[f"q{i:03d}.jpg" for i in range(len(ts))])
        ff(["-framerate","1","-i",os.path.join(pasta,"q%03d.jpg"),"-vf","scale=216:-1,tile=16x8:padding=4","-frames:v","1",os.path.join(pasta,"folha.jpg")])
        print(f"{pasta} {time.time()-t0:.0f}s")
    else:
        pasta=os.path.join(AQUI,"out","quadros"); n=int(TOTAL*FPS)
        cap([i/FPS for i in range(n)],pasta,[f"f{i:05d}.jpg" for i in range(n)])
        som=os.path.join(AQUI,"out","mix.wav"); dst=os.path.join(AQUI,"out","tutorial-pendentes.mp4")
        ff(["-framerate",str(FPS),"-i",os.path.join(pasta,"f%05d.jpg"),"-i",som,"-c:v","libx264","-preset","slow","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",dst])
        print(f"pronto {dst} {time.time()-t0:.0f}s")

#!/usr/bin/env python3
# Trilha (baião leve: zabumba, triângulo, sanfona em pad) + efeitos nos MESMOS tempos do filme.html (palavras.json + 0,4 s).
import json, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
P = json.load(open('assets/palavras.json')); OFF = .4
def W(w, n=1):
    k = 0
    for p in P:
        if p[0] == w:
            k += 1
            if k == n: return p[1] + OFF
END = P[-1][2] + OFF; DUR = END + 3.2
SR = 48000; N = int(DUR * SR); rng = np.random.default_rng(7)
MUS, FX = np.zeros((N, 2)), np.zeros((N, 2))
def tt(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, k, f, o=2): return sosfilt(butter(o, f, k, fs=SR, output='sos'), x)
def ruido(d): return rng.standard_normal(int(d * SR))
def put(buf, t0, sig, g=1., pan=0.):
    i = int(t0 * SR)
    if i >= N or i < 0 or len(sig) == 0: return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4); sig = np.stack([sig * l, sig * r], 1) * 1.414
    n = min(len(sig), N - i); sig = sig[:n] * g; k = min(480, n); sig[n - k:] *= np.linspace(1, 0, k)[:, None]; buf[i:i + n] += sig
def zabumba(g=1.):
    t = tt(.4); f = 60 + 70 * np.exp(-t / .025)
    return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .15)) * g
def bacalhau(): t = tt(.08); return filt(ruido(.08), 'bandpass', [1500, 5000]) * np.exp(-t / .015) * .5
def triangulo(aberto=True):
    d = .5 if aberto else .08; t = tt(d); x = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(3520, 1), (5150, .6), (6870, .4), (8900, .25)])
    return x * np.exp(-t / (.25 if aberto else .02)) * .12
def sanfona(notas, d):
    t = tt(d); x = np.zeros_like(t)
    for m in notas:
        for det in (-.12, .12):
            ph = (t * hz(m + det)) % 1; x += 2 * ph - 1
    x = filt(x, 'lowpass', 1800) * (1 + .15 * np.sin(2 * np.pi * 5 * t))
    return x * np.minimum(1, t / .08) * np.minimum(1, (d - t) / .15) * .035
def pluck(m, d=.4, g=1.):
    t = tt(d); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t) * np.exp(-t / .06)) * np.exp(-t / .18) * g
BPM = 112; B = 60 / BPM; COMP = 4 * B
ACO = [[55, 59, 62], [53, 57, 60], [48, 52, 55], [50, 54, 57]]   # G F C D (mixolídio)
BX = [43, 41, 36, 38]
CIDADE = W('Parece'); FIM = W('Parabéns')
t0, c = 0., 0
while t0 < DUR - 1:
    k = c % 4
    calmo = CIDADE - .3 < t0 < FIM - .5
    put(MUS, t0, sanfona([n + 12 for n in ACO[k]], COMP + .1), .9 if not calmo else .6)
    if t0 > 1.0 and t0 < END:
        for bt in range(4):
            tb = t0 + bt * B
            if not calmo:
                put(MUS, tb, zabumba(), .35 if bt in (0, 2) else .18)
                if bt in (1, 3): put(MUS, tb + B * .5, zabumba(), .14)
                put(MUS, tb + B * .5, bacalhau(), .25, .2)
            put(MUS, tb, triangulo(False), .7, -.3); put(MUS, tb + B * .5, triangulo(True), .55, -.3)
            put(MUS, tb, pluck(BX[k] + (0 if bt % 2 == 0 else 7), .35, .25), 1.)
    t0 += COMP; c += 1
put(MUS, FIM, sanfona([67, 71, 74, 79], 3.5), 1.6); put(MUS, FIM, zabumba(), .6)
# ---------- efeitos ----------
def pa(): t = tt(.25); return filt(ruido(.25), 'bandpass', [200, 1800]) * np.exp(-t / .05) * .8 + np.sin(2 * np.pi * 90 * t) * np.exp(-t / .04) * .5
def chuva(d): x = filt(ruido(d), 'bandpass', [800, 9000]); t = tt(d); return x * np.minimum(1, t / .5) * np.minimum(1, (d - t) / .6) * .18
def ronco(d, f=45): t = tt(d); x = filt(ruido(d), 'lowpass', 160) * 1.5 + np.sin(2 * np.pi * f * t) * .4; return x * np.minimum(1, t / .2) * np.minimum(1, (d - t) / .3)
def gota(m=84): t = tt(.12); f = hz(m) * (1 + 1.2 * np.exp(-t / .015)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .03)
def baque(): t = tt(.5); return np.tanh(2 * np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-t / .03)) / SR) * np.exp(-t / .12)) + filt(ruido(.5), 'lowpass', 800) * np.exp(-t / .06) * .6
def agua_corre(d): x = filt(ruido(d), 'bandpass', [300, 3000]); t = tt(d); m = 1 + .4 * np.sin(2 * np.pi * 3.1 * t) * np.sin(2 * np.pi * 1.7 * t); return x * m * np.minimum(1, t / .3) * np.minimum(1, (d - t) / .4) * .25
def pedra(): t = tt(.12); return filt(ruido(.12), 'bandpass', [1200, 5000]) * np.exp(-t / .02) + np.sin(2 * np.pi * 900 * t) * np.exp(-t / .015) * .4
def pop(m=79): t = tt(.18); f = hz(m) * (1 + .6 * np.exp(-t / .01)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .06)
def brilho(): t = tt(1.4); return sum(np.sin(2 * np.pi * hz(m) * t) for m in (88, 91, 95)) * np.exp(-t / .5) * np.minimum(1, t / .3) * .15
def rangido(): t = tt(.9); f = 300 + 120 * np.sin(2 * np.pi * 2.3 * t); x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)); return filt(x, 'bandpass', [400, 2500]) * np.minimum(1, t / .05) * np.minimum(1, (.9 - t) / .2) * .15
def whoosh(d=.5): x = filt(ruido(d), 'bandpass', [400, 3000]); t = tt(d); return x * np.sin(np.pi * t / d) ** 2 * .5
for i in range(4): put(FX, W('buraco') - .45 + i * .27, pa(), .6)
put(FX, W('chuva') - .2, chuva(W('areia') - W('chuva')), 1.)
put(FX, W('muro') - .1, ronco(1.6), .6)
put(FX, W('enxurrada') - .5, chuva(2.2), .6)
put(FX, W('enxurrada'), agua_corre(1.6), .5)
put(FX, W('barragem') - .05, pop(74), .4)
for i in range(10): put(FX, W('poros') + i * .3, gota(80 + (i * 5) % 9), .2, pan=.3)
put(FX, W('argila') - .2, whoosh(.9), .5); put(FX, W('argila') + .85, baque(), .7)
put(FX, W('inverno') - .2, chuva(W('leva') - W('inverno') + 1.2), .8)
put(FX, W('sobe'), agua_corre(2.2), .5); put(FX, W('leva') - .1, ronco(1.4, 38), .55); put(FX, W('leva') - .1, baque(), .4)

put(FX, W('sangradouro') - .3, agua_corre(3.0), .9)
put(FX, W('sol', 1) - .4, brilho(), 1.)
put(FX, W('dois') - .5, whoosh(1.2), .35)
put(FX, W('fundo', 1) - .1, pop(71), .35); put(FX, W('estreito'), pop(83), .45)
put(FX, W('enxurrada', 2) - .4, chuva(2.6), .45)
for i in range(6): put(FX, W('árvores') + i * .14, pop(76 + (i % 3) * 3), .3, pan=-.3)
put(FX, W('raízes') - .1, ronco(1.0, 70), .25)
put(FX, W('válvula') - .3, whoosh(.6), .3)
put(FX, W('solta') - .4, rangido(), 1.)
put(FX, W('solta') + .5, agua_corre(3.6), .55)
put(FX, W('correr') - .2, brilho(), .8)
put(FX, W('Parece') - .25, whoosh(.6), .5)
put(FX, W('cidade'), agua_corre(2.5), .7); put(FX, W('cidade') + .3, ronco(2.0, 40), .4)
for i in range(3): put(FX, W('lugar') - .2 + i * .12, pop(74 + i * 5), .35)
put(FX, W('Parabéns') - .3, whoosh(.7), .5)
for i in range(14): put(FX, W('Parabéns') + i * .06, pop(84 + (i * 7) % 12), .12, pan=(i % 5 - 2) / 3)

# ---------- v2: eventos da animação nova ----------
L2 = W('Então', 1); ARG = W('argila'); CAN = W('canal'); L10 = W('Então', 5)
def range_(a, n, d): return [a + i * d for i in range(n)]
def rangidoCarrinho(d): t = tt(d); f = 900 + 200 * np.sin(2 * np.pi * 3 * t); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (np.sin(2 * np.pi * 3 * t) > .6); return filt(x, 'bandpass', [600, 3000]) * .08
def bee():
    t = tt(.7); f = 480 * (1 + .04 * np.sin(2 * np.pi * 9 * t)); ph = np.cumsum(f) / SR; x = 2 * (ph % 1) - 1
    return filt(x, 'bandpass', [700, 2600]) * np.minimum(1, t / .05) * np.minimum(1, (.7 - t) / .2) * .5
def piu(m=96): t = tt(.12); f = hz(m) * (1 + .3 * np.sin(2 * np.pi * 30 * t)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / .12) * .4
for i in range(9): put(FX, L2 + .45 + i * .36 + .28, baque(), .35, pan=(-.2 if i % 2 else .2))
put(FX, 12.0, rangidoCarrinho(2.8), 1., .3)
for i in range(6): put(FX, ARG + i * .5 + .28, baque(), .55); put(FX, ARG + i * .5 + .28, pedra(), .2)
for k in range(17): put(FX, CAN - .1 + k * .17 + .2, filt(pedra(), 'lowpass', 2500), .3, pan=.25)
XA = [520, 430, 340, 250, 160, 70]
for i, x in enumerate(XA): put(FX, L10 + .45 + (560 - x) / 500 * 3.3, pop(72 + i * 2), .35, -.3)
for a in (.8, 39.2, 53.6, 65.5, 80.2):
    for j in range(5): put(FX, a + .6 + j * .37 + (j % 2) * .11, piu(94 + (j * 3) % 7), .25, pan=.5)
put(FX, W('correr') + 1.7, bee(), .7, .4); put(FX, W('Mas', 5) + 1.2, bee(), .45, .4)
for k in range(10): put(FX, .25 + k * .55 + .27, pa(), .25)
for nome, buf in (('out/musica.wav', MUS), ('out/fx.wav', FX)):
    b = buf / max(1e-9, np.abs(buf).max()) * .9; wavfile.write(nome, SR, (b * 32767).astype(np.int16))
print('ok', round(DUR, 2))

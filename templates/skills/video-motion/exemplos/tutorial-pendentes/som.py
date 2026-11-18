#!/usr/bin/env python3
# Trilha + efeitos do tutorial do Pendentes, em código (numpy/scipy), nos MESMOS tempos do filme.html.
# Saídas: out/musica.wav (trilha) e out/fx.wav (efeitos). A mixagem com a voz é no mix.py.
# Rodar: ~/.video-motion/venv/bin/python som.py
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR, DUR = 48000, 64.0
N = int(DUR * SR)
rng = np.random.default_rng(1611)
MUS, FX = np.zeros((N, 2)), np.zeros((N, 2))
BPM = 100; B = 60 / BPM


def tt(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, kind, f, order=2): return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)
def env(d, a=.003, r=.1): t = tt(d); return np.minimum(1, t / a) * np.exp(-t / r)
def ruido(d): return rng.standard_normal(int(d * SR))


def put(buf, t0, sig, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or len(sig) == 0: return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], 1) * 1.414
    n = min(len(sig), N - i); sig = sig[:n] * g
    k = min(240, n); sig[n - k:] *= np.linspace(1, 0, k)[:, None]
    buf[i:i + n] += sig


# ---------------- instrumentos ----------------
def pad(notas, d):
    t = tt(d); x = np.zeros_like(t)
    for m in notas:
        for det in (-0.07, 0.07):
            f = hz(m + det)
            x += np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t) + .12 * np.sin(2 * np.pi * 3 * f * t)
    a = np.minimum(1, t / .6) * np.minimum(1, (d - t) / .6)
    return filt(x * a, "lowpass", 2200) * .05


def pluck(m, d=.6, g=1.0):
    t = tt(d); f = hz(m)
    x = (np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .08) + .2 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / .04))
    return x * env(d, .002, .22) * g


def bumbo():
    t = tt(.35); f = 48 + 80 * np.exp(-t / .03)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16) * 1.5)


def chimbal(g=1.0): return filt(ruido(.06), "highpass", 7000) * env(.06, .001, .015) * g


def clique(g=1.0, tom=0):
    t = tt(.09)
    corpo = np.sin(2 * np.pi * (1700 + tom) * t) * np.exp(-t / .012)
    estalo = filt(ruido(.09), "bandpass", [2500, 6500]) * np.exp(-t / .004)
    grave = np.sin(2 * np.pi * 180 * t) * np.exp(-t / .02) * .5
    return (corpo * .5 + estalo * .7 + grave) * g


def whoosh(d=.45, f0=500, f1=4000, g=1.0):
    x = ruido(d); n = len(x); y = np.zeros(n); blocos = 24; h = n // blocos * 2
    for k in range(blocos * 2):
        a = k * n // (blocos * 2); seg = x[max(0, a - h // 2): a + h // 2]
        if len(seg) < 32: continue
        f = f0 * (f1 / f0) ** (k / (blocos * 2))
        yy = filt(seg, "bandpass", [f * .7, min(f * 1.3, SR / 2 - 100)]) * np.hanning(len(seg))
        y[max(0, a - h // 2): max(0, a - h // 2) + len(yy)] += yy
    t = tt(d); return y * np.sin(np.pi * t / d) ** 1.5 * g * .5


def pop(m=84, g=1.0):
    t = tt(.16); f = hz(m) * (1 + .5 * np.exp(-t / .01))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.16, .001, .05) * g


def tecla(g=1.0):
    t = tt(.05); return (filt(ruido(.05), "bandpass", [1800, 5000]) * np.exp(-t / .006) + np.sin(2 * np.pi * 900 * t) * np.exp(-t / .008) * .3) * g


def sino(notas, g=1.0):
    x = np.zeros(int(1.6 * SR))
    for i, m in enumerate(notas):
        s = pluck(m, 1.6 - i * .08, 1) ; j = int(i * .08 * SR); x[j:j + len(s)] += s
    return x * g


# ---------------- trilha: C - Am - F - G, 100 BPM, leve ----------------
ACORDES = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]]
BAIXO = [36, 33, 29, 31]
compasso = 4 * B
c = 0; t0 = 0.0
while t0 < 60.4:
    k = c % 4
    put(MUS, t0, pad(ACORDES[k], compasso + .6), 1.0)
    put(MUS, t0, pluck(BAIXO[k] + 12, compasso * .9, .35) * 1.0, .9)
    # arpejo leve (some no começo e no fim)
    if 2.0 < t0 < 58:
        arp = [ACORDES[k][i] + 12 for i in (0, 2, 1, 3, 2, 1, 3, 2)]
        for i, m in enumerate(arp):
            put(MUS, t0 + i * B / 2, pluck(m, .5, .16), 1.0, pan=(-.4 if i % 2 else .4))
    # bateria leve depois do gancho
    if 4.0 < t0 < 58:
        for bt in range(4):
            if bt in (0, 2): put(MUS, t0 + bt * B, bumbo(), .28)
            put(MUS, t0 + bt * B + B / 2, chimbal(), .12, pan=.3)
    c += 1; t0 += compasso
# acorde final
put(MUS, 60.4, pad([60, 64, 67, 72, 76], 3.6), 1.6)
put(MUS, 60.4, bumbo(), .4)

# ---------------- efeitos, nos tempos do filme ----------------
CLIQUES = [7.35, 13.55, 15.65, 16.45, 17.35, 18.15, 27.6, 32.9, 37.25, 38.15, 38.95, 40.15, 47.3, 47.7, 49.4, 50.2, 50.95]
for i, t in enumerate(CLIQUES): put(FX, t, clique(1.0, (i % 4) * 90), .55, pan=.15)
for t in [3.95, 13.85, 27.9, 30.6, 33.7, 40.15, 54.45]: put(FX, t - .12, whoosh(.45), .55, pan=-.2)
put(FX, 60.15, whoosh(.6, 300, 3000), .7)
# contadores: notas subindo (gancho e selo do menu) e descendo (lista zerando)
ESC = [72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98]
for i in range(12): put(FX, 2.9 + i * .05, pop(ESC[i], .5), .35, pan=(i - 6) / 12)
put(FX, 3.0, sino([72, 76, 79]), .25)
for i in range(12): put(FX, 10.6 + .8 * (1 - (1 - (i + 1) / 12) ** 0.25), pop(ESC[i], .5), .3)
put(FX, 10.8, sino([79, 84]), .25)
for i in range(11): put(FX, 58.5 + i * .14, pop(ESC[10 - i] - 12, .5), .3, pan=.2)
# balões de mensagem
for t, m in [(28.3, 79), (28.75, 83), (29.2, 86), (39.1, 84)]: put(FX, t, pop(m, .6), .45, pan=.3)
# abas trocando a lista
for t in [16.45, 17.35, 18.15]: put(FX, t + .05, whoosh(.3, 1200, 5000), .25, pan=.4)
# digitação
for i in range(29): put(FX, 47.8 + i * (1.0 / 29) + rng.random() * .01, tecla(.8 + .4 * rng.random()), .35, pan=.1)
# marcadores amarelos (um risco de caneta)
for t in [21.3, 24.1, 36.3, 42.6, 43.3, 44.8, 54.0]: put(FX, t, whoosh(.22, 2500, 6000), .18, pan=.2)
# risco do Rafael e saída da linha
put(FX, 54.9, whoosh(.3, 1500, 6000), .3); put(FX, 55.1, whoosh(.45, 3000, 600), .4, pan=.5)
put(FX, 55.7, pop(88, .7), .4)
# sucesso
put(FX, 51.6, sino([72, 76, 79, 84]), .45)
put(FX, 60.0, sino([76, 79, 84, 88]), .45)
put(FX, 60.6, bumbo(), .5)

# reverb curto de sala na trilha e nos efeitos
ir = ruido(1.2) * np.exp(-tt(1.2) / .25); ir = filt(ir, "lowpass", 5000); ir /= np.sqrt((ir ** 2).sum())
for buf, w in ((MUS, .25), (FX, .18)):
    for ch in range(2):
        buf[:, ch] += fftconvolve(buf[:, ch], ir)[:N] * w

def salvar(nome, x):
    x = x / max(1e-9, np.abs(x).max()) * .9
    wavfile.write(nome, SR, (x * 32767).astype(np.int16))
salvar("out/musica.wav", MUS); salvar("out/fx.wav", FX)
print("ok", DUR, "s")

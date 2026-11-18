#!/usr/bin/env python3
# Trilha (viola sertaneja + pad, tensa à noite) + ambiente (cigarras de dia, grilos à noite) + efeitos nos tempos do filme.
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
END = P[-1][2] + OFF; DUR = END + 3.4
SR = 48000; N = int(DUR * SR); rng = np.random.default_rng(11)
MUS, FX, AMB = np.zeros((N, 2)), np.zeros((N, 2)), np.zeros((N, 2))
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
L = [W('Seu'), W('Se'), W('Então', 1), W('Mas', 1), W('Então', 2), W('Mas', 2), W('Então', 3), W('Mas', 3), W('Então', 4), W('Mas', 4), W('Então', 5), W('Parece'), W('Parabéns')]
NOITE0, NOITE1 = L[7] - .25, L[9] - .25
# ---------- instrumentos ----------
def viola(m, d=1.2, g=1.):  # corda dupla (viola caipira): duas cordas levemente desafinadas, ataque brilhante
    t = tt(d); x = np.zeros_like(t)
    for det, a in ((0, 1), (.08, .7), (12, .25)):
        f = hz(m + det); x += a * (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) * np.exp(-t / .15) + .3 * np.sin(6 * np.pi * f * t) * np.exp(-t / .06))
    return x * np.exp(-t / .5) * np.minimum(1, t / .003) * g * .18
def pad(notas, d, brilho=1500):
    t = tt(d); x = np.zeros_like(t)
    for m in notas:
        for det in (-.07, .07): x += np.sin(2 * np.pi * hz(m + det) * t) + .3 * np.sin(4 * np.pi * hz(m + det) * t)
    return filt(x, 'lowpass', brilho) * np.minimum(1, t / .8) * np.minimum(1, (d - t) / .8) * .045
def bumbo(): t = tt(.35); return np.tanh(1.5 * np.sin(2 * np.pi * np.cumsum(55 + 70 * np.exp(-t / .03)) / SR) * np.exp(-t / .14))
def ganza(): t = tt(.07); return filt(ruido(.07), 'bandpass', [3000, 9000]) * np.exp(-t / .02) * .25
BPM = 96; B = 60 / BPM; COMP = 4 * B
ACO = [[50, 57, 62, 66], [48, 55, 60, 64], [47, 54, 59, 62], [45, 52, 57, 61]]  # Ré mixolídio/menor do sertão
ARP = [0, 2, 1, 3, 2, 1, 3, 1]
t0, c = 0., 0
while t0 < DUR - .5:
    k = c % 4; noite = NOITE0 - .5 < t0 < NOITE1; fim = t0 > L[12] - 1; fato = L[11] - 1 < t0 < L[12] - 1
    if noite:
        put(MUS, t0, pad([38, 45, 50], COMP + .5, 600), 1.4)
        for bt in (0, 2): put(MUS, t0 + bt * B, bumbo(), .25)  # coração
        put(MUS, t0 + B * .3, bumbo(), .15); put(MUS, t0 + 2 * B + B * .3, bumbo(), .15)
    else:
        put(MUS, t0, pad([n + 12 for n in ACO[k]], COMP + .5), 1.0 if not fato else .8)
        for i, a in enumerate(ARP):
            put(MUS, t0 + i * B / 2, viola(ACO[k][a] + 12, 1.0, .9 if i % 2 == 0 else .6), 1., pan=(-.35 if i % 2 else .35))
        if t0 > 1.5 and not fato:
            for bt in range(4): put(MUS, t0 + bt * B, bumbo(), .22 if bt in (0, 2) else .1); put(MUS, t0 + bt * B + B / 2, ganza(), .5, .3); put(MUS, t0 + bt * B + B * .75, ganza(), .3, .3)
    t0 += COMP; c += 1
put(MUS, L[12], pad([62, 66, 69, 74], 3.6, 2400), 1.8); put(MUS, L[12], bumbo(), .5)
for i, m in enumerate([74, 78, 81, 86]): put(MUS, L[12] + .1 + i * .12, viola(m, 2.0, 1.2), 1.)
# ---------- ambiente: cigarras de dia, grilos à noite ----------
def cigarra(d):
    t = tt(d); x = filt(ruido(d), 'bandpass', [4200, 6500]) * (.6 + .4 * np.sin(2 * np.pi * 38 * t)) * (.7 + .3 * np.sin(2 * np.pi * .4 * t))
    return x * np.minimum(1, t / 1) * np.minimum(1, (d - t) / 1) * .05
def grilo(d):
    t = tt(d); car = np.sin(2 * np.pi * 4300 * t); env = (np.sin(2 * np.pi * 28 * t) > .2) * (np.sin(2 * np.pi * 1.6 * t) > 0)
    return car * env * np.minimum(1, t / .5) * np.minimum(1, (d - t) / .5) * .025
put(AMB, 0, cigarra(NOITE0 + .2), 1., -.2); put(AMB, 0, cigarra(NOITE0 + .2)[::-1].copy(), .7, .3)
put(AMB, NOITE0, grilo(NOITE1 - NOITE0 + .3), 1., -.4); put(AMB, NOITE0 + .37, grilo(NOITE1 - NOITE0), .8, .5)
put(AMB, NOITE1, cigarra(L[11] - NOITE1), .8, -.2)
# ---------- efeitos ----------
def whoosh(d=.5): x = filt(ruido(d), 'bandpass', [400, 3500]); t = tt(d); return x * np.sin(np.pi * t / d) ** 2 * .55
def baque(): t = tt(.5); return np.tanh(2 * np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-t / .03)) / SR) * np.exp(-t / .12)) + filt(ruido(.5), 'lowpass', 800) * np.exp(-t / .06) * .6
def motor(d): t = tt(d); f = 38 * (1 - .5 * t / d); ph = np.cumsum(f) / SR; x = np.sign(np.sin(2 * np.pi * ph)) * .5 + filt(ruido(d), 'lowpass', 300); return filt(x, 'lowpass', 900) * np.minimum(1, t / .1) * np.minimum(1, (d - t) / .2) * .4
def chiado(d): t = tt(d); return filt(ruido(d), 'highpass', 2500) * np.exp(-t / (d * .6)) * .25
def bip(m=84, d=.15): t = tt(d); return np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / .005) * np.minimum(1, (d - t) / .03) * .4
def gota(m=84): t = tt(.12); f = hz(m) * (1 + 1.2 * np.exp(-t / .015)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .03)
def pa(): t = tt(.25); return filt(ruido(.25), 'bandpass', [200, 1800]) * np.exp(-t / .05) * .8 + np.sin(2 * np.pi * 90 * t) * np.exp(-t / .04) * .5
def agua(d): x = filt(ruido(d), 'bandpass', [400, 2500]); t = tt(d); return x * (1 + .4 * np.sin(2 * np.pi * 3.1 * t)) * np.minimum(1, t / .4) * np.minimum(1, (d - t) / .4) * .18
def chocalho(d): t = tt(d); x = filt(ruido(d), 'bandpass', [3500, 9000]) * (.5 + .5 * np.sign(np.sin(2 * np.pi * 55 * t))); return x * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .1) * .4
def pop(m=79): t = tt(.18); f = hz(m) * (1 + .6 * np.exp(-t / .01)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .06)
def passo(): t = tt(.12); return filt(ruido(.12), 'bandpass', [150, 1200]) * np.exp(-t / .03) * .5
def latido(): t = tt(.18); f = 520 * (1 - .3 * t / .18); return filt(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 'bandpass', [400, 1800]) * np.exp(-t / .07) * .35
def estrela(): t = tt(.6); return sum(np.sin(2 * np.pi * hz(m) * t) for m in (84, 88, 91)) * np.exp(-t / .2) * .15
for b in L[1:]: put(FX, b - .5, whoosh(.55), .7)
put(FX, 0, motor(W('quebrou') + .1), 1.); put(FX, W('quebrou') + .05, baque(), .7); put(FX, W('quebrou') + .7, chiado(2.5), .8)
put(FX, W('Sem') - .1, bip(76), .55); put(FX, W('Sem') + .12, bip(70), .55); put(FX, W('quarenta'), whoosh(1.0), .3)
for k in range(10): put(FX, W('dois') + .2 + k * .32, passo(), .4, .2)
for k in range(14): put(FX, L[1] + .2 + k * .42, passo(), .35, .1)
put(FX, W('garrafa') - .1, agua(1.2), .8)
for k in range(5): put(FX, W('manhã') - .2 + k * .35, passo(), .35); put(FX, W('tarde') - .1 + k * .35, passo(), .35)
for i in range(3): put(FX, W('regra') - .4 + i * .15, pop(76 + i * 4), .5)
for i in range(4): put(FX, W('acaba') + i * .09, gota(70 + i), .3)
put(FX, W('acaba') + .5, gota(88), .5)
for k in range(9): put(FX, W('cava') - .1 + k * .26, pa(), .55, -.1)
put(FX, W('brotar') - .1, agua(2.5), 1.)
for i in range(6): put(FX, W('brotar') + i * .4, gota(86 + i % 3 * 3), .25)
put(FX, W('espinho') - .1, pop(90), .7)
put(FX, W('fruta') - .1, pop(72), .6)
put(FX, W('batatas') - .2, agua(2.0), .4)
put(FX, W('chocalho') - .1, filt(chocalho(W('recua') - W('chocalho') + .6), 'lowpass', 6500), .55, .4)
for k in range(5): put(FX, W('recua') + .1 + k * .55, passo(), .3, -.2)
put(FX, W('enxerga') - .2, whoosh(.4), .4)
put(FX, W('ninguém') - .2, whoosh(2.2), .4)
for k in range(16): put(FX, L[10] + .1 + k * .55, passo(), .3)
put(FX, W('fumaça') - .2, estrela(), 1.)
put(FX, W('umbu') - .1, estrela(), .8); put(FX, W('árvore') - .1, pop(81), .4)
put(FX, W('cangaceiros') - .2, baque(), .3)
for k in range(5): put(FX, W('cangaceiros') + .2 + k * .3, pa(), .3)
for i in range(3): put(FX, L[12] + .4 + i * .3, latido(), .5, .3)
def norm(b): return b / max(1e-9, np.abs(b).max()) * .9
MUS = MUS + AMB * 6
for nome, buf in (('out/musica.wav', MUS), ('out/fx.wav', FX)): wavfile.write(nome, SR, (norm(buf) * 32767).astype(np.int16))
print('ok', round(DUR, 2))

#!/usr/bin/env python3
# Trilha original sintetizada em codigo (sem musica de terceiros), ja na grade do roteiro:
# comeca num tempo forte em t=0, entao BPM e inicio sao exatos e nao precisa de `hf beats`.
# Bumbo, chimbal, palma, baixo, pad e arpejo seguindo i-VI-III-VII (menor) ou I-V-vi-IV (maior), semente fixa.
#
# uso pelo montar.py: sintetizar(caminho_wav, bpm, duracao_s, clima="energico"|"calmo", tom="A", modo="menor"|"maior")
# uso solto:          python3 trilha_sintetica.py saida.wav 120 30 [clima] [tom] [modo]
import sys, wave
import numpy as np

SR = 48000
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
PROG = {"menor": [(0, "m"), (8, "M"), (3, "M"), (10, "M")], "maior": [(0, "M"), (7, "M"), (9, "m"), (5, "M")]}

def hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)

def env(n, a, r):                                 # ataque linear + queda exponencial (em amostras)
    e = np.ones(n); a = max(1, int(a * SR)); e[:a] = np.linspace(0, 1, a)
    e[a:] = np.exp(-np.arange(n - a) / max(1, r * SR)); return e

def passa_baixa(x, fc):                           # 1 polo, suficiente pra amaciar serra
    k = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc = (1 - k) * x[i] + k * acc; y[i] = acc
    return y

def serra(f, n, rng, desafina=0.0):
    t = np.arange(n) / SR; fase = rng.random()
    return 2 * (((f * (1 + desafina)) * t + fase) % 1) - 1

def sintetizar(saida, bpm, dur, clima="energico", tom="A", modo="menor"):
    rng = np.random.default_rng(7)
    B = 60 / bpm; N = int((dur + 1) * SR); L = np.zeros(N); R = np.zeros(N)
    raiz = 45 + NOTAS.get(tom.upper(), 9)          # A2 = 45
    prog = PROG.get(modo, PROG["menor"]); energico = clima != "calmo"
    def soma(sinal, t0, vol=1.0, pan=0.0):
        i = int(t0 * SR); j = min(N, i + len(sinal))
        if i >= N: return
        s = sinal[: j - i] * vol
        L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))
    # timbres
    nk = int(.45 * SR); tk = np.arange(nk) / SR
    bumbo = np.sin(2 * np.pi * np.cumsum(45 + 75 * np.exp(-tk * 28)) / SR) * env(nk, .002, .16)
    nh = int(.06 * SR); chimbal = np.diff(rng.standard_normal(nh + 1)) * env(nh, .001, .012) * .35
    npal = int(.22 * SR); palma = passa_baixa(np.diff(rng.standard_normal(npal + 1)), 3500) * env(npal, .002, .06) * 1.4
    batidas = int(dur / B) + 2
    for k in range(batidas):
        t = k * B; compasso, tempo = divmod(k, 4)
        if energico or tempo in (0, 2): soma(bumbo, t, .9)
        if energico and tempo in (1, 3): soma(palma, t, .5, .1)
        soma(chimbal, t + B / 2, .5 if energico else .3, -.25)
        if energico: soma(chimbal, t + B / 4 * 3, .22, .25)
    for c in range(batidas // 4 + 1):
        grau, q = prog[c % 4]; t0 = c * 4 * B; f0 = raiz + grau
        terca = 3 if q == "m" else 4
        # baixo em colcheias (energico) ou minimas (calmo)
        passo = B / 2 if energico else B * 2
        for m in range(int(4 * B / passo)):
            n = int(passo * .9 * SR)
            s = (np.sin(2 * np.pi * hz(f0 - 12) * np.arange(n) / SR) + .3 * serra(hz(f0 - 12), n, rng)) * env(n, .005, passo * .6)
            soma(passa_baixa(s, 900), t0 + m * passo, .32)
        # pad: acorde com serras desafinadas, ataque lento
        n = int(4 * B * SR); pad = np.zeros(n)
        for iv in (0, terca, 7, 12):
            for d in (-.004, .004): pad += serra(hz(f0 + 12 + iv), n, rng, d)
        e = np.minimum(1, np.arange(n) / (SR * .4)) * np.minimum(1, (n - np.arange(n)) / (SR * .3))
        soma(passa_baixa(pad * e, 1400 if energico else 900), t0, .045)
        # arpejo em semicolcheias com pan alternado
        notas = [f0 + 24, f0 + 24 + terca, f0 + 31, f0 + 36]
        for m in range(16 if energico else 8):
            n = int(.18 * SR); nt = notas[m % 4]
            s = np.sin(2 * np.pi * hz(nt) * np.arange(n) / SR) * env(n, .002, .07)
            soma(s, t0 + m * (B / 4 if energico else B / 2), .11, .35 if m % 2 else -.35)
    est = np.stack([L, R], 1); est /= max(1e-9, np.abs(est).max()) / .89
    with wave.open(saida, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((est * 32767).astype("<i2").tobytes())

if __name__ == "__main__":
    a = sys.argv[1:]
    sintetizar(a[0], float(a[1]), float(a[2]), *(a[3:6]))
    print("ok", a[0])

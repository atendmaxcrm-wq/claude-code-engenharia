#!/usr/bin/env python3
# Voz (0,4 s de atraso) + trilha com sidechain pela voz + efeitos -> out/mix.wav a -14 LUFS
import subprocess
D = 64
f = [
    f'[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,adelay=400|400,volume=1.5,apad=whole_dur={D},asplit=2[voz][sc]',
    '[1:a]aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.5[mus0]',
    '[mus0][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=400[mus]',
    '[2:a]volume=0.55[fx]',
    f'[mus][voz][fx]amix=inputs=3:normalize=0,atrim=0:{D},afade=t=out:st={D-1.5}:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11[out]',
]
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'assets/narracao.mp3', '-i', 'out/musica.wav', '-i', 'out/fx.wav',
                '-filter_complex', ';'.join(f), '-map', '[out]', '-ar', '48000', 'out/mix.wav'], check=True)
print('ok out/mix.wav')

#!/usr/bin/env python3
# Preset VELVET : voix normalisée + SFX de sfx-plan.json, chaque son calé sur son attaque.
#   python3 PKG/preset/mixer.py v1                                    écrit v1/mix.m4a
#   python3 PKG/preset/mixer.py v1 v1/export/RUSH-velvet-v1-rendu.mp4 v1/export/RUSH-velvet-v1.mp4    pose le mix sur le rendu, image intacte
import glob, json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; SR, FPS = 48000, 30
CRETE = dict(hook=-14, gros=-14, rouge=-12, flash=-14, cta=-12)   # crête de chaque son en dB, sous la voix
def lire(cmd):
    return np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', *cmd, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2)
voix = lire(['-i', glob.glob(f'{OUT}/composition/assets/*-cuts.mp4')[0], '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11']).copy()
sons = {}
for n in CRETE:
    x = lire(['-i', f'{HERE}/sfx/{n}.mp3']); m = abs(x).max(axis=1); p = m.max()
    a = max(0, int(np.argmax(m > p * .1)) - 48)
    sons[n] = x[a:] * (10 ** (CRETE[n] / 20) / p)
for e in json.load(open(f'{OUT}/sfx-plan.json')):
    i = int(e['f'] / FPS * SR); s = sons[e['son']][:len(voix) - i]; voix[i:i + len(s)] += s
voix.tofile(f'{OUT}/mix.f32')
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', f'{OUT}/mix.f32', '-af', 'alimiter=limit=0.84:level=disabled', '-c:a', 'aac', '-b:a', '256k', f'{OUT}/mix.m4a'], check=True)
os.remove(f'{OUT}/mix.f32')
if len(sys.argv) > 3:
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', sys.argv[2], '-i', f'{OUT}/mix.m4a', '-map', '0:v', '-map', '1:a', '-c', 'copy', '-shortest', '-movflags', '+faststart', sys.argv[3]], check=True)

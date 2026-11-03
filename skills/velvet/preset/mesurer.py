#!/usr/bin/env python3
# Tableau des durées réellement visibles, à sortir avant tout rendu : python3 PKG/preset/mesurer.py v1 [-a]
# Sans -a, seules les lignes trop brèves s'affichent : gros mot sous 0,4 s, sous-titre sous 0,25 s. Le rythme suit la parole : à regarder, pas à corriger d'office.
import html, re, sys
page = open(sys.argv[1] + '/composition/index.html').read(); ko = 0
for cl, t0, dur, corps in re.findall(r'<div class="cap (s-\w+)[^"]*" id="[^"]+"[^>]*?data-t0="([\d.]+)" data-dur="([\d.]+)".*?<span class="tx">(.*?)</span>(?:<svg|</div>)', page):
    if cl == 's-btn': continue
    gros = cl in ('s-big', 's-rbig'); mn = .4 if gros else .25; d = float(dur)
    t = html.unescape(re.sub(r'<[^>]+>', '', corps)); vu = d < mn - .005; ko += vu
    if '-a' in sys.argv or vu: print(f"{'✗' if vu else ' '} {float(t0):6.2f}s  {'GROS' if gros else 'sous-titre':10} {d:5.2f}s  {t}")
print(f'{ko} ligne(s) à regarder (la référence C0209 validée en a 17)')

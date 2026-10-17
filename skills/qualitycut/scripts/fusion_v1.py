# Recolle depuis la première transcription (vidéo entière) les passages que la transcription par morceaux a perdus :
# zones d'au moins 1 s où la 1re transcription a des mots et la seconde aucun.
import json, sys, os, re
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
HALLU = re.compile(r"titrage|ST' ?501|Amara|Merci d'avoir regardé|Abonnez", re.I)
for c in sys.argv[1:]:
    segs = [s for s in json.load(open(f'{W}/transcription/{c}.json')) if not HALLU.search(s['text'])]
    v1 = json.load(open(f'{W}/transcription/v1/{c}.json'))
    t2 = sorted(w['start'] for s in segs for w in s['words'])
    def couvert(t): return any(abs(t - u) < 0.8 for u in t2)
    orphelins = [w for s in v1 for w in s['words'] if not couvert(w['start'])]
    zones, cur = [], []
    for w in orphelins:
        if cur and w['start'] - cur[-1]['end'] > 1.0: zones.append(cur); cur = []
        cur.append(w)
    if cur: zones.append(cur)
    zones = [z for z in zones if z[-1]['end'] - z[0]['start'] >= 1.0 and len(z) >= 3]
    for z in zones:
        a, b = z[0]['start'] - 0.05, z[-1]['end'] + 0.05
        segs = [dict(s, words=[w for w in s['words'] if not (a <= w['start'] <= b)]) for s in segs]
        segs = [dict(s, start=s['words'][0]['start'], end=s['words'][-1]['end']) for s in segs if s['words']]
        segs.append({'start': z[0]['start'], 'end': z[-1]['end'], 'text': ' '.join(w['word'].strip() for w in z), 'words': z, 'v1': True})
        print(f"  {c} {a:6.2f}-{b:6.2f} recollé : {' '.join(w['word'].strip() for w in z)}")
    segs.sort(key=lambda s: s['start'])
    json.dump(segs, open(f'{W}/transcription/{c}.json', 'w'), ensure_ascii=False, indent=1)
    print(c, len(zones), 'zone(s) recollée(s)')

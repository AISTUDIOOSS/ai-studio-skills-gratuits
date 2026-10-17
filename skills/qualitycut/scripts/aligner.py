# Alignement forcé (MMS_FA) des mots de la transcription verbatim : début et fin de chaque mot à ~20 ms près.
import json, sys, os, re, unicodedata
import torch, torchaudio
from num2words import num2words
from torchaudio.pipelines import MMS_FA as bundle

W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
PONCT = ',.?!;:…'

def lettres(t):
    t = re.sub(r'\d+', lambda m: ' ' + num2words(int(m.group(0)), lang='fr') + ' ', t)
    t = unicodedata.normalize('NFKD', t.lower().replace('’', "'"))
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z']", ' ', t)
    return [p for p in t.split() if p.strip("'")]

def mots_whisper(clip):
    segs = json.load(open(f'{W}/transcription/{clip}.json'))
    mots = []
    for s in segs:
        for w in s.get('words', []):
            t = w['word'].strip()
            if not t:
                continue
            # « 5 » + « 000, » → « 5000, » ; « 10 » « 000 » idem
            if mots and re.fullmatch(r'000[' + PONCT + ']*', t) and re.fullmatch(r'\d+', mots[-1]['texte']):
                mots[-1]['texte'] += t; mots[-1]['w_fin'] = w['end']; continue
            mots.append({'texte': t, 'w_debut': w['start'], 'w_fin': w['end'], 'proba': round(w.get('probability', 0), 2)})
    return mots

def emission_par_morceaux(model, wav):
    N = wav.shape[1]; morceau, ctx = 20 * 16000, 2 * 16000
    parts = []
    with torch.inference_mode():
        for d in range(0, N, morceau):
            a, b = max(0, d - ctx), min(N, d + morceau + ctx)
            em, _ = model(wav[:, a:b])
            f0 = (d - a) // 320
            nf = (min(N, d + morceau) - d) // 320
            parts.append(em[0, f0:f0 + nf])
    return torch.cat(parts)

def aligner(clip, model, tok, ali):
    mots = mots_whisper(clip)
    import numpy as np, scipy.io.wavfile as wf
    sr, a = wf.read(f'{W}/audio/{clip}-16k.wav')
    wav = torch.from_numpy(a.astype(np.float32) / 32768.0).unsqueeze(0)
    em = emission_par_morceaux(model, wav)
    ratio = wav.shape[1] / em.shape[0] / 16000
    # liste de « mots » pour l'aligneur : une étoile entre chaque mot absorbe les « euh » non transcrits
    seq, origine = ['*'], [None]
    for i, m in enumerate(mots):
        for p in lettres(m['texte']):
            seq.append(p); origine.append(i)
        seq.append('*'); origine.append(None)
    spans = ali(em, tok(seq))
    for i in range(len(mots)):
        mots[i]['debut'] = mots[i]['fin'] = None; mots[i]['score'] = None
    for s, o in zip(spans, origine):
        if o is None:
            continue
        d, f = s[0].start * ratio, s[-1].end * ratio
        sc = sum(x.score * (x.end - x.start) for x in s) / max(1, sum(x.end - x.start for x in s))
        m = mots[o]
        m['debut'] = d if m['debut'] is None else min(m['debut'], d)
        m['fin'] = f if m['fin'] is None else max(m['fin'], f)
        m['score'] = round(sc if m['score'] is None else min(m['score'], sc), 3)
    # ponctuation seule (« ? ») : on la colle au mot d'avant
    for i, m in enumerate(mots):
        if m['debut'] is None:
            j = i - 1
            m['debut'] = m['fin'] = mots[j]['fin'] if j >= 0 else m['w_debut']
    for m in mots:
        m['debut'] = round(m['debut'], 3); m['fin'] = round(m['fin'], 3)
    json.dump(mots, open(f'{W}/transcription/{clip}-aligne.json', 'w'), ensure_ascii=False, indent=0)
    print('aligné', clip, len(mots), 'mots', flush=True)

if __name__ == '__main__':
    model = bundle.get_model().eval()
    tok, ali = bundle.get_tokenizer(), bundle.get_aligner()
    for clip in sys.argv[1:]:
        aligner(clip, model, tok, ali)

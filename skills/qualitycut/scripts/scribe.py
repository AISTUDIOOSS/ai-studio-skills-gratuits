# Transcription avec ElevenLabs Scribe (seul moteur du pack, Mac et Windows).
# Clé : variable ELEVENLABS_API_KEY ou fichier ~/.config/elevenlabs/key (jamais affichée).
# transcrire(son, sr) renvoie des segments au format attendu par les autres scripts :
# [{'start', 'end', 'text', 'words': [{'word', 'start', 'end', 'probability'}]}], temps en secondes.
import io, json, math, os, sys, time, uuid, urllib.request, urllib.error, wave
import numpy as np

URL = 'https://api.elevenlabs.io/v1/speech-to-text'
FIN_PHRASE, PAUSE, MAX_MOTS = '.?!…', 1.0, 30
FICHIER_CLE = os.path.expanduser('~/.config/elevenlabs/key')


def cle():
    k = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if not k and os.path.exists(FICHIER_CLE):
        k = open(FICHIER_CLE, encoding='utf-8').read().strip()
    if not k:
        sys.exit("Pas de clé ElevenLabs. Crée-la sur elevenlabs.io (Developers → API Keys), "
                 f"puis enregistre-la dans {FICHIER_CLE}.")
    return k


def _wav(son, sr):
    """Tableau numpy (float -1..1 ou int16) → octets WAV mono 16 bits."""
    x = np.asarray(son)
    if x.ndim > 1: x = x.mean(axis=1)
    if x.dtype != np.int16: x = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    b = io.BytesIO()
    with wave.open(b, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(sr)); w.writeframes(x.tobytes())
    return b.getvalue()


def _envoyer(audio, model, k, evenements):
    champs = {'model_id': model, 'language_code': 'fra', 'tag_audio_events': 'true' if evenements else 'false',
              'timestamps_granularity': 'word', 'diarize': 'false'}
    limite = uuid.uuid4().hex
    corps = b''.join(f'--{limite}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode() for n, v in champs.items())
    corps += (f'--{limite}\r\nContent-Disposition: form-data; name="file"; filename="son.wav"\r\n'
              'Content-Type: audio/wav\r\n\r\n').encode() + audio + f'\r\n--{limite}--\r\n'.encode()
    req = urllib.request.Request(URL, data=corps, method='POST', headers={
        'xi-api-key': k, 'Content-Type': f'multipart/form-data; boundary={limite}'})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read().decode('utf-8'))


def brut(son, sr, evenements=False):
    """Appel Scribe sur un extrait. Réessaie en cas de coupure réseau ; scribe_v2 puis scribe_v1."""
    k, audio, derniere = cle(), _wav(son, sr), ''
    for essai in range(3):
        for model in ('scribe_v2', 'scribe_v1'):
            try:
                return _envoyer(audio, model, k, evenements)
            except urllib.error.HTTPError as e:
                derniere = f'{model} : HTTP {e.code} {e.read()[:300].decode("utf-8", "replace")}'
                if e.code in (401, 403):
                    sys.exit(f"Clé ElevenLabs refusée ({e.code}). Vérifie la clé dans {FICHIER_CLE}.")
                if e.code == 402 or 'quota' in derniere.lower():
                    sys.exit("Crédits ElevenLabs épuisés : recharge le compte sur elevenlabs.io puis relance.")
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                derniere = f'{model} : {e}'
        time.sleep(3 * (essai + 1))
    sys.exit(f'ElevenLabs ne répond pas : {derniere}')


def mots(data, decalage=0.0):
    return [{'word': ' ' + w['text'].strip(), 'start': round(decalage + w['start'], 3), 'end': round(decalage + w['end'], 3),
             'probability': round(math.exp(w['logprob']), 3) if 'logprob' in w else 1.0}
            for w in data.get('words', []) if w.get('type') == 'word' and w['text'].strip()]


def segments(ms):
    segs, cur = [], []
    for w in ms:
        if cur and (w['start'] - cur[-1]['end'] > PAUSE or len(cur) >= MAX_MOTS):
            segs.append(cur); cur = []
        cur.append(w)
        if w['word'].strip()[-1:] in FIN_PHRASE: segs.append(cur); cur = []
    if cur: segs.append(cur)
    return [{'start': s[0]['start'], 'end': s[-1]['end'], 'text': ' '.join(w['word'].strip() for w in s), 'words': s}
            for s in segs]


def transcrire(son, sr, decalage=0.0):
    """Segments (temps décalés de `decalage` secondes) d'un extrait. Extrait trop court → aucun mot."""
    if len(son) < 0.3 * sr: return []
    return segments(mots(brut(son, sr), decalage))


def texte(son, sr):
    return ' '.join(s['text'] for s in transcrire(son, sr)).strip()


if __name__ == '__main__':
    # python scribe.py --tester : vérifie que la clé marche (envoie 1 s de silence, coût quasi nul)
    if '--tester' in sys.argv:
        brut(np.zeros(16000, dtype=np.int16), 16000)
        print('clé ElevenLabs OK')

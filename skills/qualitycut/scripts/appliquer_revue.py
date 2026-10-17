"""Applique des réunions de plans documentées, après revue sonore explicite ; les indices ne détectent pas les mots non transcrits."""
import json
import os
from pathlib import Path
import sys


def appliquer(data, review):
    if data.get('fps') != 30:
        raise ValueError('Revue locale attendue à 30 i/s')
    result = json.loads(json.dumps(data))
    segments = result['segments']
    for join in review.get('joins', []):
        left, right = join['leftLastWord'], join['rightFirstWord']
        if type(left) is not int or type(right) is not int or right != left + 1:
            raise ValueError('Les mots de jonction doivent être consécutifs')
        if not isinstance(join.get('reason'), str) or not join['reason'].strip():
            raise ValueError('Motif de revue requis')
        if join.get('classification') not in ('parole_utile', 'continuite_voix'):
            raise ValueError('Fusion refusée : contenu ajouté non identifié comme utile')
        evidence = join.get('audioReview', {})
        if evidence.get('method') not in ('ecoute_humaine', 'ecoute_multimodale'):
            raise ValueError('Fusion refusée : écoute réelle requise, ASR seul insuffisant')
        if not isinstance(evidence.get('observation'), str) or not evidence['observation'].strip():
            raise ValueError('Fusion refusée : observation sonore requise')
        # Attestation de revue fournie par l'appelant, pas preuve automatique d'écoute.
        # Déjà réunis : ne rien changer.
        if any(s['mots'][0] <= left < right <= s['mots'][1] for s in segments):
            continue
        matches = [i for i in range(len(segments)-1)
                   if segments[i]['mots'][1] == left and segments[i+1]['mots'][0] == right]
        if len(matches) != 1:
            raise ValueError(f'Jonction introuvable ou ambiguë : {left}/{right}')
        i = matches[0]
        a, b = segments[i:i+2]
        if not a['in'] < a['out'] <= b['in'] < b['out']:
            raise ValueError('Bornes de plans invalides')
        segments[i:i+2] = [dict(a, out=b['out'], mots=[a['mots'][0], b['mots'][1]],
                                texte=a['texte']+' '+b['texte'])]
    result['qualitycutReview'] = review
    return result


def main():
    rush = sys.argv[1]
    if Path(rush).name != rush:
        raise ValueError('Nom de rush attendu, sans chemin')
    folder = Path(os.environ.get('MONTAGE_DOSSIER', '.')).expanduser().resolve() / 'montage'
    review_path = folder / f'{rush}-revue.json'
    if not review_path.exists():
        print('Aucune exception de revue'); return
    target = folder / f'{rush}-coupes.json'
    result = appliquer(json.loads(target.read_text()), json.loads(review_path.read_text()))
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(target)
    print(f'Revue appliquée : {len(result["segments"])} plans')


if __name__ == '__main__':
    main()

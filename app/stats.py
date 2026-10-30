"""Nettoyage des données, indicateurs et interprétation des écoutes.

Ce module concentre la partie « analyse » du projet : il nettoie les
titres importés, calcule les indicateurs (KPI) et rédige en français
ce que les chiffres racontent, au lieu de se contenter d'afficher
des graphiques.
"""

import csv
import io
import re
from collections import Counter

MIN_YEAR = 1900
MAX_YEAR = 2030


def clean_text(value):
    """Nettoie un texte : espaces superflus supprimés, casse harmonisée."""
    if value is None:
        return ""
    cleaned = re.sub(r"\s+", " ", str(value)).strip()
    return cleaned


def normalize_track(title, artist):
    """Renvoie le couple (titre, artiste) nettoyé, prêt à comparer."""
    return clean_text(title), clean_text(artist)


def is_valid_track(title, artist, duration_seconds, year=None):
    """Vérifie qu'un titre est exploitable avant de l'enregistrer.

    Renvoie (True, "") si tout va bien, sinon (False, raison du rejet).
    """
    title, artist = normalize_track(title, artist)
    if not title:
        return False, "titre vide"
    if not artist:
        return False, "artiste vide"
    try:
        duration = int(duration_seconds)
    except (TypeError, ValueError):
        return False, "durée invalide"
    if duration <= 0:
        return False, "durée nulle ou négative"
    if year not in (None, ""):
        try:
            year = int(year)
        except (TypeError, ValueError):
            return False, "année invalide"
        if not MIN_YEAR <= year <= MAX_YEAR:
            return False, "année hors plage"
    return True, ""


def find_duplicate(tracks, title, artist):
    """Cherche un doublon (même titre, même artiste, casse indifférente)."""
    title, artist = normalize_track(title, artist)
    for track in tracks:
        t_title, t_artist = normalize_track(track.title, track.artist)
        if t_title.lower() == title.lower() and t_artist.lower() == artist.lower():
            return track
    return None


def compute_kpis(playlists, tracks):
    """Calcule les indicateurs clés à partir des playlists et des titres."""
    total_plays = sum(t.play_count for t in tracks)
    total_duration = sum(t.duration_seconds for t in tracks)
    favorites = sum(1 for t in tracks if t.favorite)
    plays_by_artist = Counter()
    plays_by_genre = Counter()
    for track in tracks:
        plays_by_artist[track.artist] += track.play_count
        plays_by_genre[track.genre or "Inconnu"] += track.play_count
    top_tracks = sorted(tracks, key=lambda t: (-t.play_count, t.title))[:5]
    return {
        "total_playlists": len(playlists),
        "total_tracks": len(tracks),
        "total_favorites": favorites,
        "total_plays": total_plays,
        "total_duration_seconds": total_duration,
        "total_duration_minutes": round(total_duration / 60) if total_duration else 0,
        "avg_duration_seconds": round(total_duration / len(tracks)) if tracks else 0,
        "top_artist": plays_by_artist.most_common(1)[0][0] if plays_by_artist else None,
        "top_genre": plays_by_genre.most_common(1)[0][0] if plays_by_genre else None,
        "top_tracks": top_tracks,
        "plays_by_genre": dict(plays_by_genre),
        "plays_by_artist": dict(plays_by_artist),
    }


def plays_by_playlist(playlists):
    """Nombre d'écoutes cumulées pour chaque playlist."""
    result = {}
    for playlist in playlists:
        result[playlist.name] = sum(t.play_count for t in playlist.tracks)
    return result


def interpret(kpis):
    """Rédige en français ce que les chiffres montrent.

    L'idée : un tableau de bord ne sert à rien sans une lecture des
    résultats. Chaque phrase est générée à partir des vrais chiffres.
    """
    lines = []
    if kpis["total_tracks"] == 0:
        return ["Aucun titre enregistré pour le moment : ajoutez des titres "
                "ou importez un fichier CSV pour voir vos statistiques."]
    lines.append(
        f"Vous avez {kpis['total_tracks']} titre(s) répartis dans "
        f"{kpis['total_playlists']} playlist(s), pour "
        f"{kpis['total_duration_minutes']} minutes de musique au total."
    )
    if kpis["total_plays"]:
        lines.append(
            f"Au total, {kpis['total_plays']} écoute(s) ont été enregistrées, "
            "ce qui montre quelles musiques reviennent vraiment dans vos oreilles."
        )
    else:
        lines.append(
            "Aucune écoute n'a encore été comptabilisée : utilisez le bouton "
            "« Écouté » sur un titre pour alimenter vos statistiques."
        )
    if kpis["top_artist"]:
        lines.append(f"L'artiste le plus écouté est {kpis['top_artist']}.")
    if kpis["top_genre"]:
        lines.append(f"Le genre dominant de vos écoutes est {kpis['top_genre']}.")
    if kpis["total_favorites"]:
        lines.append(
            f"Vous avez mis {kpis['total_favorites']} titre(s) en favori : "
            "ce sont vos valeurs sûres, celles que vous gardez sous la main."
        )
    return lines


def parse_csv(text):
    """Lit un CSV de titres et sépare les lignes valides des rejets.

    Colonnes attendues : titre, artiste, genre, duree_secondes, annee.
    Renvoie (lignes_valides, rejets) où chaque rejet porte sa raison.
    """
    reader = csv.DictReader(io.StringIO(text))
    valid, rejected = [], []
    seen = set()
    for number, row in enumerate(reader, start=2):
        title, artist = normalize_track(
            row.get("titre", ""), row.get("artiste", "")
        )
        genre = clean_text(row.get("genre", "")) or "Inconnu"
        duration = row.get("duree_secondes", "")
        year = clean_text(row.get("annee", "")) or None
        ok, reason = is_valid_track(title, artist, duration, year)
        if not ok:
            rejected.append({"ligne": number, "titre": title, "raison": reason})
            continue
        key = (title.lower(), artist.lower())
        if key in seen:
            rejected.append({"ligne": number, "titre": title, "raison": "doublon"})
            continue
        seen.add(key)
        valid.append({
            "title": title,
            "artist": artist,
            "genre": genre,
            "duration_seconds": int(duration),
            "year": int(year) if year else None,
        })
    return valid, rejected


def svg_bar_chart(data, width=560, height=220):
    """Dessine un graphique en barres simple, en SVG, sans dépendance."""
    if not data:
        return ""
    items = sorted(data.items(), key=lambda item: -item[1])
    max_value = max(value for _, value in items) or 1
    bar_height = 24
    gap = 10
    label_width = 150
    chart_width = width - label_width - 50
    parts = [f'<svg width="{width}" height="{height}" '
             'xmlns="http://www.w3.org/2000/svg" role="img">']
    for index, (label, value) in enumerate(items):
        y = index * (bar_height + gap) + 10
        bar = round(chart_width * value / max_value)
        parts.append(
            f'<text x="0" y="{y + 16}" font-size="13">{label}</text>'
            f'<rect x="{label_width}" y="{y}" width="{bar}" '
            f'height="{bar_height}" fill="#0f766e" />'
            f'<text x="{label_width + bar + 6}" y="{y + 16}" '
            f'font-size="13">{value}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)

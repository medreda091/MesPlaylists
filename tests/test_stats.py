"""Tests du nettoyage, des indicateurs et de l'interprétation."""

from app import db
from app.models import Playlist, Track
from app.stats import (
    clean_text,
    compute_kpis,
    find_duplicate,
    interpret,
    is_valid_track,
    parse_csv,
    svg_bar_chart,
)


def test_nettoyage_espaces_superflus():
    assert clean_text("  Blinding   Lights  ") == "Blinding Lights"


def test_titre_invalide_sans_duree():
    ok, raison = is_valid_track("Titre", "Artiste", 0)
    assert not ok
    assert raison == "durée nulle ou négative"


def test_annee_hors_plage_rejetee():
    ok, _ = is_valid_track("Titre", "Artiste", 180, 1800)
    assert not ok


def test_doublon_detecte_malgre_la_casse(app):
    tracks = Track.query.all()
    assert find_duplicate(tracks, "titre un", "artiste a") is not None
    assert find_duplicate(tracks, "Autre titre", "Artiste A") is None


def test_indicateurs(app):
    kpis = compute_kpis(Playlist.query.all(), Track.query.all())
    assert kpis["total_playlists"] == 1
    assert kpis["total_tracks"] == 2
    assert kpis["total_plays"] == 14
    assert kpis["total_favorites"] == 1
    assert kpis["total_duration_minutes"] == 8
    assert kpis["top_artist"] == "Artiste A"
    assert kpis["top_tracks"][0].title == "Titre Un"


def test_interpretation_mentionne_les_vrais_chiffres(app):
    kpis = compute_kpis(Playlist.query.all(), Track.query.all())
    texte = " ".join(interpret(kpis))
    assert "2 titre(s)" in texte
    assert "Artiste A" in texte


def test_import_csv_separe_valides_et_rejets():
    csv_text = ("titre,artiste,genre,duree_secondes,annee\n"
                "Bon titre,Artiste,Pop,200,2020\n"
                "Sans duree,Artiste,Pop,,2020\n"
                "Bon titre,Artiste,Pop,200,2020\n")
    valid, rejected = parse_csv(csv_text)
    assert len(valid) == 1
    assert len(rejected) == 2
    assert rejected[0]["raison"] == "durée invalide"
    assert rejected[1]["raison"] == "doublon"


def test_graphique_svg_contient_les_valeurs():
    svg = svg_bar_chart({"Pop": 10, "Rock": 4})
    assert "<svg" in svg
    assert "Pop" in svg
    assert ">10<" in svg

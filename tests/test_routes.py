"""Tests des routes : playlists, titres, statistiques, import."""

from app import db
from app.models import Playlist, Track


def test_accueil_affiche_les_indicateurs(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test" in response.data
    assert b"14" in response.data  # total des écoutes de la fixture


def test_creation_playlist(client):
    response = client.post("/playlists", data={"name": "Soirée"})
    assert response.status_code == 302
    assert Playlist.query.filter_by(name="Soirée").first() is not None


def test_ajout_titre_et_doublon_refuse(client):
    playlist = Playlist.query.first()
    url = f"/playlists/{playlist.id}/tracks"
    data = {"title": "Nouveau", "artist": "Artiste B",
            "genre": "Pop", "duration_seconds": "180", "year": "2021"}
    assert client.post(url, data=data).status_code == 302
    assert Track.query.filter_by(title="Nouveau").count() == 1
    # Même titre, même artiste, espaces et casse différents : refusé.
    data["title"] = "  nouveau "
    assert client.post(url, data=data).status_code == 302
    assert Track.query.filter_by(title="Nouveau").count() == 1


def test_ecoute_et_favori(client):
    track = Track.query.filter_by(title="Titre Deux").first()
    client.post(f"/tracks/{track.id}/play")
    client.post(f"/tracks/{track.id}/favorite")
    db.session.refresh(track)
    assert track.play_count == 5
    assert track.favorite is True


def test_page_statistiques(client):
    response = client.get("/stats")
    assert response.status_code == 200
    assert "Ce que les chiffres montrent".encode() in response.data
    assert b"<svg" in response.data


def test_import_csv_avec_rapport(client):
    playlist = Playlist.query.first()
    data = {
        "playlist_id": str(playlist.id),
        "fichier": (
            __import__("io").BytesIO(
                b"titre,artiste,genre,duree_secondes,annee\n"
                b"Importe,Artiste C,Pop,210,2022\n"
                b"Rate,Artiste C,Pop,,2022\n"
            ),
            "titres.csv",
        ),
    }
    response = client.post("/import", data=data,
                           content_type="multipart/form-data")
    assert response.status_code == 200
    assert "1 titre(s) ajouté(s)".encode() in response.data
    assert Track.query.filter_by(title="Importe").first() is not None

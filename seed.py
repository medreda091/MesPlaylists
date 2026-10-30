"""Remplit la base avec des playlists et des titres d'exemple."""

from app import create_app, db
from app.models import Playlist, Track

app = create_app()

EXEMPLES = [
    ("Coups de cœur", "Les titres qu'on réécoute sans se lasser", [
        ("Blinding Lights", "The Weeknd", "Pop", 200, 2020, 24, True),
        ("Bohemian Rhapsody", "Queen", "Rock", 354, 1975, 18, True),
        ("Shape of You", "Ed Sheeran", "Pop", 233, 2017, 15, False),
    ]),
    ("Sport", "Pour tenir le rythme pendant l'entraînement", [
        ("Eye of the Tiger", "Survivor", "Rock", 245, 1982, 12, False),
        ("Lose Yourself", "Eminem", "Rap", 326, 2002, 20, True),
    ]),
    ("Détente", "Le soir, volume bas", [
        ("Clair de Lune", "Debussy", "Classique", 300, 1905, 6, False),
        ("Weightless", "Marconi Union", "Ambient", 480, 2011, 9, False),
    ]),
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for name, description, tracks in EXEMPLES:
        playlist = Playlist(name=name, description=description)
        db.session.add(playlist)
        db.session.flush()
        for title, artist, genre, duration, year, plays, favorite in tracks:
            db.session.add(Track(
                title=title, artist=artist, genre=genre,
                duration_seconds=duration, year=year,
                play_count=plays, favorite=favorite,
                playlist_id=playlist.id,
            ))
    db.session.commit()
    print("Base remplie : 3 playlists, 7 titres.")

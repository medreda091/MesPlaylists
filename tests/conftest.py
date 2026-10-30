"""Configuration partagée des tests."""

import pytest

from app import create_app, db
from app.models import Playlist, Track


@pytest.fixture
def app():
    """Application de test, base SQLite en mémoire."""
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with application.app_context():
        db.create_all()
        playlist = Playlist(name="Test", description="Playlist de test")
        db.session.add(playlist)
        db.session.flush()
        db.session.add(Track(
            title="Titre Un", artist="Artiste A", genre="Pop",
            duration_seconds=200, year=2020, play_count=10,
            favorite=True, playlist_id=playlist.id,
        ))
        db.session.add(Track(
            title="Titre Deux", artist="Artiste A", genre="Rock",
            duration_seconds=300, year=2019, play_count=4,
            playlist_id=playlist.id,
        ))
        db.session.commit()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    """Client de test Flask."""
    return app.test_client()

"""Modèles de données : playlists et titres."""

from datetime import datetime

from . import db


class Playlist(db.Model):
    """Une playlist regroupe plusieurs titres."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tracks = db.relationship(
        "Track", backref="playlist", cascade="all, delete-orphan", lazy=True
    )

    def __repr__(self):
        return f"<Playlist {self.name}>"


class Track(db.Model):
    """Un titre écouté, rattaché à une playlist."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(80), default="Inconnu")
    duration_seconds = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    favorite = db.Column(db.Boolean, default=False)
    play_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlist.id"), nullable=False)

    def __repr__(self):
        return f"<Track {self.title} - {self.artist}>"

    @property
    def duration_display(self):
        """Durée affichée au format minutes:secondes."""
        minutes, seconds = divmod(self.duration_seconds, 60)
        return f"{minutes}:{seconds:02d}"

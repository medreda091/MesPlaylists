"""Routes de l'application : playlists, titres, statistiques, import."""

from flask import Blueprint, redirect, render_template, request, url_for

from . import db
from .models import Playlist, Track
from .stats import (
    clean_text,
    compute_kpis,
    find_duplicate,
    interpret,
    is_valid_track,
    parse_csv,
    plays_by_playlist,
    svg_bar_chart,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Page d'accueil : playlists et indicateurs globaux."""
    playlists = Playlist.query.order_by(Playlist.created_at.desc()).all()
    tracks = Track.query.all()
    kpis = compute_kpis(playlists, tracks)
    return render_template("index.html", playlists=playlists, kpis=kpis)


@bp.route("/playlists", methods=["POST"])
def create_playlist():
    """Crée une playlist puis revient à l'accueil."""
    name = clean_text(request.form.get("name", ""))
    if name:
        db.session.add(Playlist(
            name=name, description=clean_text(request.form.get("description", ""))
        ))
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/playlists/<int:playlist_id>")
def playlist_detail(playlist_id):
    """Détail d'une playlist et ses titres."""
    playlist = Playlist.query.get_or_404(playlist_id)
    return render_template("playlist.html", playlist=playlist)


@bp.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    """Supprime une playlist et tous ses titres."""
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("/playlists/<int:playlist_id>/tracks", methods=["POST"])
def add_track(playlist_id):
    """Ajoute un titre nettoyé, en refusant les doublons."""
    playlist = Playlist.query.get_or_404(playlist_id)
    title = request.form.get("title", "")
    artist = request.form.get("artist", "")
    ok, _reason = is_valid_track(
        title, artist,
        request.form.get("duration_seconds", ""),
        request.form.get("year", "") or None,
    )
    if ok and not find_duplicate(playlist.tracks, title, artist):
        from .stats import normalize_track

        clean_title, clean_artist = normalize_track(title, artist)
        db.session.add(Track(
            title=clean_title,
            artist=clean_artist,
            genre=clean_text(request.form.get("genre", "")) or "Inconnu",
            duration_seconds=int(request.form.get("duration_seconds")),
            year=int(request.form.get("year")) if request.form.get("year") else None,
            playlist_id=playlist.id,
        ))
        db.session.commit()
    return redirect(url_for("main.playlist_detail", playlist_id=playlist.id))


@bp.route("/tracks/<int:track_id>/play", methods=["POST"])
def play_track(track_id):
    """Compte une écoute de plus pour un titre."""
    track = Track.query.get_or_404(track_id)
    track.play_count += 1
    db.session.commit()
    return redirect(url_for("main.playlist_detail", playlist_id=track.playlist_id))


@bp.route("/tracks/<int:track_id>/favorite", methods=["POST"])
def favorite_track(track_id):
    """Ajoute ou retire un titre des favoris."""
    track = Track.query.get_or_404(track_id)
    track.favorite = not track.favorite
    db.session.commit()
    return redirect(url_for("main.playlist_detail", playlist_id=track.playlist_id))


@bp.route("/tracks/<int:track_id>/delete", methods=["POST"])
def delete_track(track_id):
    """Supprime un titre d'une playlist."""
    track = Track.query.get_or_404(track_id)
    playlist_id = track.playlist_id
    db.session.delete(track)
    db.session.commit()
    return redirect(url_for("main.playlist_detail", playlist_id=playlist_id))


@bp.route("/stats")
def stats():
    """Tableau de bord : KPI, graphiques et interprétation en français."""
    playlists = Playlist.query.all()
    tracks = Track.query.all()
    kpis = compute_kpis(playlists, tracks)
    return render_template(
        "stats.html",
        kpis=kpis,
        interpretation=interpret(kpis),
        chart_genres=svg_bar_chart(kpis["plays_by_genre"]),
        chart_playlists=svg_bar_chart(plays_by_playlist(playlists)),
    )


@bp.route("/import", methods=["GET", "POST"])
def import_csv():
    """Importe des titres depuis un fichier CSV, avec rapport qualité."""
    playlists = Playlist.query.all()
    result = None
    if request.method == "POST":
        playlist = Playlist.query.get_or_404(int(request.form.get("playlist_id")))
        uploaded = request.files.get("fichier")
        if uploaded:
            valid, rejected = parse_csv(uploaded.read().decode("utf-8"))
            added = 0
            for row in valid:
                if find_duplicate(playlist.tracks, row["title"], row["artist"]):
                    rejected.append({
                        "ligne": "?", "titre": row["title"],
                        "raison": "déjà présent dans la playlist",
                    })
                    continue
                db.session.add(Track(playlist_id=playlist.id, **row))
                added += 1
            db.session.commit()
            result = {"added": added, "rejected": rejected}
    return render_template("import.html", playlists=playlists, result=result)

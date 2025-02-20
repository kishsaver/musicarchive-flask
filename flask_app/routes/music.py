import os
import librosa
import numpy as np
from datetime import datetime
from flask import (
    current_app, Blueprint, render_template, request, 
    redirect, url_for, flash, session, send_from_directory
)
from flask_app.models import db, Music, MusicPlayData
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from functools import wraps

music_bp = Blueprint('music', __name__)

def login_required(f):
    """ログインを必須にする"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename: str) -> bool:
    """fileの拡張子チェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@music_bp.route('/recorder', methods=['GET', 'POST'])
@login_required
def recorder() -> str:
    """楽曲の登録を行う"""
    if request.method == 'POST':
        song_name: str = request.form.get('song_name')
        artist_name: str = request.form.get('artist_name')
        category: str = request.form.get('category')
        music_file = request.files.get('music_file')

        if music_file and allowed_file(music_file.filename):
            file_name: str = secure_filename(music_file.filename)
            file_path: str = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
            music_file.save(file_path)
            
            y, sr = librosa.load(file_path, sr=22050)
            bpm: float
            bpm = librosa.beat.beat_track(y=y, sr=sr)

            music = Music(
                song_name=song_name,
                artist_name=artist_name,
                category=category,
                bpm=int(bpm[0]),
                file_name=file_name,
                music_user_id=session['user_id']
            )

            try:
                db.session.add(music)
                db.session.commit()
                flash('楽曲が正常に登録されました', 'success')
                return redirect(url_for('music.list'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'データベースエラーが発生しました: {str(e)}', 'error')
            finally:
                db.session.close()

    return render_template('recorder.html')

@music_bp.route('/list', methods=['GET', 'POST'])
@login_required
def list() -> str:
    """楽曲の一覧を表示する"""
    user_id: int = session['user_id']
    musics: list[Music] = []

    if request.method == 'POST':
        music_id: str | None = request.form.get('music_id')
        if not music_id:
            flash('削除する楽曲を選択してください', 'error')
            return redirect(url_for('music.list'))
        try:
            music: Music | None = Music.query.filter_by(id=music_id, music_user_id=user_id).first()
            if not music:
                flash('楽曲が1件も登録されていません', 'error')
                return redirect(url_for('music.list'))

            db.session.delete(music)
            db.session.commit()
            flash('楽曲が正常に削除されました', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'データベースエラーが発生しました: {str(e)}', 'error')

    try:
        musics = Music.query.filter_by(music_user_id=user_id).all()
    except SQLAlchemyError as e:
        flash(f'データベースエラーが発生しました: {str(e)}', 'error')
    finally:
        db.session.close()

    return render_template('list.html', musics=musics, login_user_id=user_id)

@music_bp.route('/uploads/<file_name>')
def uploaded_file(file_name: str):
    """ファイル名を返すだけのエンドポイント（html出力を伴わない実装の例）"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], file_name, mimetype='audio/mpeg')

@music_bp.route('/log_play_time', methods=['POST'])
def log_play_time() -> tuple[dict[str, str], int]:
    """音楽ファイルの再生日時を取得し、データベースに保存"""
    data: dict = request.json
    play_timedate: str = data.get('play_timedate')
    music_id: str = data.get('music_id')

    if play_timedate and music_id:
        try:
            play_datetime: datetime = datetime.strptime(play_timedate, "%Y-%m-%dT%H:%M:%S.%fZ")
            music: Music = Music.query.filter_by(id=music_id).first()
            if not music:
                return {"status": "error", "message": "Music file not found"}, 404

            log = MusicPlayData(
                play_music_id=music.id,
                play_user_id=session['user_id'],
                play_datetime=play_datetime
            )

            db.session.add(log)
            db.session.commit()

            return {"status": "success", "message": "Play time logged"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "message": f"Database error: {str(e)}"}, 500

    return {"status": "error", "message": "Invalid data"}, 400

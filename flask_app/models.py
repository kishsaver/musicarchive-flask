# ORM
from flask_sqlalchemy import SQLAlchemy
#パスワードハッシュ化関連
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy() #ORMの定義

class User(db.Model):
    """ユーザテーブル"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    musics = db.relationship('Music', backref='User', lazy=True)
    playdata = db.relationship('MusicPlayData', backref='User', lazy=True)

    # パスワードハッシュ系、ルーティングファイル側で実装も可
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.user_id}>'

class Music(db.Model):
    """楽曲テーブル"""
    __tablename__ = 'musics'
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    music_user_id = db.Column(db.String(80), db.ForeignKey('users.user_id'), nullable=False)
    playdata = db.relationship('MusicPlayData', backref='Music', lazy=True)

class MusicPlayData(db.Model):
    """楽曲再生データ"""
    __tablename__ = "playdata"
    id = db.Column(db.Integer, primary_key=True)
    play_music_id = db.Column(db.Integer, db.ForeignKey('musics.id'), nullable=False)
    play_user_id = db.Column(db.String(80), db.ForeignKey('users.user_id'), nullable=False)
    play_datetime = db.Column(db.DateTime, nullable=False)


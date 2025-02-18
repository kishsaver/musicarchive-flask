from flask import Flask
# dbモデル
from flask_app.models import db
# ルーティングファイル
from flask_app.routes.auth import auth_bp
from flask_app.routes.music import music_bp
from flask_app.routes.analysis import analysis_bp

def create_app():
    app = Flask(__name__, static_folder="./static") # Flaskのインスタンス生成、css/jsのフォルダ指定

    #SQLite3を使うように、MySQL等ならIPアドレス等を記述
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@mysql-db:3306/musicarchive'
    #セッション利用に秘密鍵が必要
    app.config['SECRET_KEY'] = 'dev'
    #ファイルアップロード関係
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = '.mp3, .wav'
    db.init_app(app)
    #ルーティングファイルをエンドポイントとして登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(analysis_bp)

    return app

app = create_app()

with app.app_context():
    db.create_all()

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
from flask import Blueprint, session, jsonify, current_app
from flask_app.models import db, Music, MusicPlayData
from sqlalchemy.exc import SQLAlchemyError

analysis_bp = Blueprint('analysis', __name__)

def get_play_history(user_id):
    current_app.logger.debug(f"Fetching play history for user_id: {user_id}")

    try:
        play_data = (
            db.session.query(MusicPlayData, Music)
            .join(Music, Music.id == MusicPlayData.play_music_id)
            .filter(MusicPlayData.play_user_id == user_id)
            .all()
        )

        current_app.logger.debug(f"Query result count: {len(play_data)}")

        records = []
        for play, music in play_data:
            current_app.logger.debug(f"Found record: {play}, {music}")
            records.append({
                "play_datetime": play.play_datetime,
                "hour": play.play_datetime.hour,
                "category": music.category,
                "bpm": music.bpm,
                "song_name": music.song_name,
                "artist_name": music.artist_name,
                "file_name": music.file_name
            })

        current_app.logger.debug(f"Total records added: {len(records)}")

        df = pd.DataFrame(records)
        current_app.logger.debug("Generated DataFrame:")
        current_app.logger.debug(df)

        return df

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error: {e}")
        return pd.DataFrame()

    finally:
        db.session.close()

def preprocess_data(df):
    df["time_of_day"] = pd.cut(
        df["hour"], 
        bins=[0,6,12,18,24],
        labels = ["midnight", "morning", "afternoon", "night"], 
        include_lowest=True
        )

    encoder = OneHotEncoder(sparse_output=False)
    category_encoded = encoder.fit_transform(df[["category"]])
    category_df = pd.DataFrame(
        category_encoded, 
        columns=encoder.get_feature_names_out(["category"])
        )

    df = pd.concat([df, category_df], axis=1)
    df.drop(columns=["category"], inplace=True)

    return df, encoder

def train_kmeans(df):
    """ユーザーごとの時間帯とBPMを元にクラスタリングを行う"""
    feature_cols = ["hour", "bpm"] + [col for col in df.columns if "category_" in col]
    X = df[feature_cols]

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X)

    return kmeans, df

def train_random_forest(df):
    """ランダムフォレストで楽曲の推薦モデルを作成"""
    feature_cols = ["hour", "bpm"] + [col for col in df.columns if "category_" in col]
    X = df[feature_cols]
    y = df["cluster"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

@analysis_bp.route('/analysis', methods=['GET'])
def recommend_ml():
    """機械学習を用いた楽曲推薦"""
    user_id = session["user_id"]
    current_hour = datetime.now().hour

    # データ取得
    df = get_play_history(user_id)
    if df.empty:
        return jsonify({"message": "再生履歴がありません。"})

    # データ前処理
    df, encoder = preprocess_data(df)
    
    # クラスタリング
    kmeans, df = train_kmeans(df)

    # ランダムフォレスト学習
    model = train_random_forest(df)

    # 現在時刻に適したクラスタを予測
    input_data = pd.DataFrame([[current_hour, df["bpm"].mean()]], columns=["hour", "bpm"])
    input_data[encoder.get_feature_names_out(["category"])] = 0  # カテゴリを全てゼロに
    predicted_cluster = model.predict(input_data)[0]

    # 該当クラスタの楽曲を取得
    recommended_song = df[df["cluster"] == predicted_cluster].sample(1)

    if not recommended_song.empty:
        result = recommended_song.iloc[0]
        return jsonify({
            "song_name": result["song_name"],
            "artist_name": result["artist_name"],
            "bpm": int(result["bpm"]),
            "file_name": result["file_name"]
        })
    else:
        return jsonify({"message": "適した楽曲が見つかりませんでした。"})    
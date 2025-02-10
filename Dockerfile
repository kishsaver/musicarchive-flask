FROM python:3.11.5-slim-bullseye

WORKDIR /flask_app

# ホストのファイルをコンテナの/flask_appディレクトリにコピー
COPY . .
# ホストのrequirements.txtをコンテナのflask_appディレクトリにコピー
RUN pip install -r requirements.txt

# Flaskのデバッグモードを有効にする（Pythonやhtmlの変更がブラウザのリロードだけで反映される）
ENV FLASK_DEBUG=1
# Flaskのアプリケーションファイルを指定
ENV FLASK_APP=main.py

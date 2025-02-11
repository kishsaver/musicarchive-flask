# musicarchive-flask
## 25年度 システム構築講義 ハンズオン資料

- ブランチについて  
  
`main` リリース版、どういう状況になってるかは不明

`php_transplant` php版を単純に移植しただけ、機能の追加などなし  

その他はかいはつちう~

=================================
musicarchive flask版  

DBはSQLite3を利用  

- ライブラリのインストール  
`git clone`したリポジトリ内で`pip install -r requirements.txt  

- Flaskアプリケーションの実行   

`pip install -r requirements.txt`  

でライブラリを入れたあと、

`python3 -m flask_app.main`

=================================

アプリケーションディレクトリからの`tree`  

flask_app  
├── __init__.py  
├── main.py  
├── models.py  
├── routes  
│   ├── auth.py  
│   └── music.py  
└── templates  
    ├── index.html  
    ├── list.html  
    ├── recorder.html  
    └── register.html  

- `__init__.py`：必須モジュール、コンフィグ情報、DB初期化  

- `main.py`：アプリケーションの起動  

- `models.py`：DBクラスの定義  

- `routes/auth.py`：認証関連のエンドポイント  

- `routes/music.py`：楽曲管理関連のエンドポイント  

- `templates/ hoge .html` :php版の命名規則に準拠  

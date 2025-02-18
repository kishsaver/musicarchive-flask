#__init__.pyで定義したFlaskアプリの情報
from flask_app import app

#DBのイニシャライズとWeb鯖の起動
if __name__ == '__main__':
    app.run(debug=True)
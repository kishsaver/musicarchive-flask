#__init__.pyで定義したFlaskアプリの情報
from flask_app import app, db

#DBのイニシャライズとWeb鯖の起動
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
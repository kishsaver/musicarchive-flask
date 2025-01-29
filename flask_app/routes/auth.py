#Flask関連、良いレイアウトではないが、説明用に
from flask import (
    Blueprint, #ルーティングファイルの分割・登録
    render_template, #HTMLファイルのレンダリング
    request, # HTTPリクエスト
    redirect, # エンドポイントへのリダイレクト
    url_for, # エンドポイントの指定
    flash, #flashメッセージ（phpで言うprint）
    session #セッション管理
    )
#DBモデル
from flask_app.models import db, User
#DBエラーハンドリング
from sqlalchemy.exc import SQLAlchemyError

#ルーティングファイルとして定義
auth_bp = Blueprint('auth', __name__)

#"/"エンドポイント、auth.indexとして呼び出される
@auth_bp.route('/', methods=['GET', 'POST'])
def index(): #本当はlogin等のが良いが、PHP版に準拠
    """ログイン処理"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        try:
            #Userテーブルから、user_idが一致するレコードを取得
            user = User.query.filter_by(user_id=user_id).first()
            if user and user.check_password(password):
                #セッション変数の定義
                session['user_id'] = user.user_id
                #routes/music.pyの、recorderエンドポイントにリダイレクト
                return redirect(url_for('music.recorder'))
            
            #flashメッセージの表示、2つめの引数でカテゴリ定義が可能
            flash('ユーザIDまたはパスワードに不備があります', 'error')
            return render_template('index.html')
        
        except SQLAlchemyError as e:
            flash(f'データベースエラーが発生しました: {str(e)}', 'error')
            return render_template('index.html')

        finally:
            # db接続を閉じる
            db.session.close()

    return render_template('index.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザの新規登録"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if confirm_password != password:
            flash('パスワードとパスワード（再入力）が一致しません', 'error')

        try:
            existing_user = User.query.filter_by(user_id=user_id).first()
            if existing_user:
                flash('このIDは既に登録済みのため別のIDで登録してください', 'error')
                return render_template('register.html')

            # ユーザーの作成と保存
            user = User(user_id=user_id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('ユーザの登録が正常に完了しました', 'success')
            return redirect(url_for('auth.index'))

        except SQLAlchemyError as e:
            db.session.rollback()  # 変更をロールバック
            flash(f'データベースエラーが発生しました: {str(e)}', 'error')
            return render_template('register.html')

        finally:
            db.session.close()

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """セッション変数の削除"""
    session.pop('user_id', None) #セッション変数削除
    return redirect(url_for('auth.index'))

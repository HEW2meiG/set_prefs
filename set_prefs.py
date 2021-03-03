import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from flask import jsonify
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'User'
    
    User_id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(64), unique=True, index=True, nullable=False)
    username = db.Column(db.String(64), index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    picture_path = db.Column(db.Text, default='default.jpeg', nullable=False)
    prof_comment = db.Column(db.Text)
    default_ShippingAddress_id = db.Column(db.Integer)
    default_pay_way = db.Column(db.Integer, default=1, nullable=False)
    default_Credit_id = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True, nullable=True)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

class Sell(db.Model):

    __tablename__ = 'Sell'

    Sell_id = db.Column(db.Integer, primary_key=True) 
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    sell_title = db.Column(db.String(255), nullable=False)  
    key1 = db.Column(db.String(255), nullable=False) 
    key2 = db.Column(db.String(255), nullable=False)  
    key3 = db.Column(db.String(255), nullable=False) 
    sell_comment = db.Column(db.Text, nullable=False)  
    price = db.Column(db.Integer, nullable=False)
    item_picture_path = db.Column(db.Text, default='default.png', nullable=False)
    genre = db.Column(db.Integer, nullable=False)
    item_state = db.Column(db.Integer, nullable=False)
    postage = db.Column(db.Integer, nullable=False)  
    send_way = db.Column(db.Integer, nullable=False)  
    consignor = db.Column(db.String(64), nullable=False)  
    schedule = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text)
    deal_status = db.Column(db.Integer, nullable=False)
    sell_flg = db.Column(db.Boolean,default=True, nullable=False)
    is_active = db.Column(db.Boolean,default=True, nullable=False)
    has_sent = db.Column(db.Boolean,default=False, nullable=False)
    has_got = db.Column(db.Boolean,default=False, nullable=False)
    create_at = db.Column(db.DateTime,default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime,default=datetime.now, nullable=False)
    user = db.relationship('User', backref='sell', lazy='joined', uselist=False)


class Buy(db.Model):

    __tablename__ = 'Buy'

    Buy_id = db.Column(db.Integer, primary_key=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    pay_way = db.Column(db.Integer, nullable=False)
    Credit_id = db.Column(db.Integer, nullable=False)
    ShippingAddress_id = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @classmethod
    def buy_exists_user_id(cls, User_id, Sell_id):
        """
        Sell_idとユーザーIDが一致する購入情報レコードを抽出し、
        レコードが存在すればTrue、
        存在しなければFalseを返す
        """
        record = cls.query.filter(
                    and_(
                        cls.Sell_id == Sell_id,
                        cls.User_id == User_id
                    )
                ).first()
        if record:
            return True
        else:
            return False


class Likes(db.Model):

    __tablename__ = 'Likes'

    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), primary_key=True, )
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), primary_key=True)
    create_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @classmethod
    def liked_exists_user_id(cls, User_id, Sell_id):
        """
        Sell_idとユーザーIDが一致するいいねレコードを抽出し、
        レコードが存在すればTrue、
        存在しなければFalseを返す
        """
        record = cls.query.filter(
                    and_(
                        cls.Sell_id == Sell_id,
                        cls.User_id == User_id
                    )
                ).first()
        if record:
            return True
        else:
            return False


class BrowsingHistory(db.Model):

    __tablename__ = 'BrowsingHistory'

    BrowsingHistory_id = db.Column(db.Integer, primary_key=True)
    Sell_id = db.Column(db.Integer, db.ForeignKey('Sell.Sell_id'), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('User.User_id'), nullable=False)
    create_at = db.Column(db.DateTime,default=datetime.now, nullable=False)
    update_at = db.Column(db.DateTime,default=datetime.now, nullable=False)

    @classmethod
    def b_history_exists(cls, User_id, Sell_id):
        """
        User_idとSell_idが一致するレコードが存在していれば
        (ユーザーが商品を閲覧していれば)
        True,
        存在していなければFalseを返す
        """
        record = cls.query.filter(
                    and_(
                        cls.User_id == User_id,
                        cls.Sell_id == Sell_id
                    )
                ).first()
        if record:
            return True
        else:
            return False

prefs={}

def set_prefs():
    with db.app.app_context():
        global prefs
        prefs={}
        users = User.query.all()
        items = Sell.query.all()
        for user in users:
            userid = user.User_id
            prefs.setdefault(userid,{})
            for item in items:
                itemid = item.Sell_id
                rating = 0
                bought = Buy.buy_exists_user_id(userid, itemid)
                if bought:
                    rating += 3
                else:
                    b_history = BrowsingHistory.b_history_exists(userid, itemid)
                    if b_history:
                        rating += 1
                    liked = Likes.liked_exists_user_id(userid, itemid)
                    if liked:
                        rating += 2
                prefs[userid][itemid] = rating
        print("load prefs")

basedir = os.path.abspath(os.path.dirname(__name__))

class Config(object):
    JOBS = [
        {
            'id': 'job',
            'func': set_prefs,
            'replace_existing': True,
            'trigger': 'interval',
            'minutes': 1,
            'max_instances': 1
        }
    ]

    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///' + os.path.join(basedir, 'data.sqlite'))
    }

    SCHEDULER_API_ENABLED = True


app = Flask(__name__)
app.config.from_object(Config())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

db.app = app
db.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)



@app.route('/get_prefs',methods=['GET'])
def get_prefs():
    print("response")
    return jsonify(prefs)


if __name__ == '__main__':
    try:
        scheduler.start()
    except KeyboardInterrupt:
        pass
    app.run(debug=True, threaded=True, port=8000)
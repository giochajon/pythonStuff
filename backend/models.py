from backend import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Users(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, index=True)
    email = db.Column(db.Text)
    num_saved_trails = db.Column(db.Integer)
    joined = db.Column(db.Date)

    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.num_saved_trails = 0
        self.joined = datetime.today()


class Login(db.Model):

    __tablename__ = "login"

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(128))
    parent_username = db.Column(db.Text)
    parent_id = db.Column(db.Integer,
                          db.ForeignKey('users.id',
                                        ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False
                          )

    def __init__(self, password, parent_id, parent_username):
        self.parent_id = parent_id
        self.hash = generate_password_hash(password)
        self.parent_username = parent_username

    def check_password(self, password):
        return check_password_hash(self.hash, password)


class SavedTrails(db.Model):

    __tablename__ = "saved_trails"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id',
                                      ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False
                        )
    trail_data = db.Column(db.String)
    trail_id = db.Column(db.Integer)

    def __init__(self, user_id, trail_id, trail_data):
        self.user_id = user_id
        self.trail_id = trail_id
        self.trail_data = trail_data

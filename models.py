from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(255),nullable=False, unique=True)
    password=db.Column(db.String(255),nullable=False)
    game=db.relationship("Game",backref="user",lazy=True)
class Game(db.Model):
    __tablename__="game"
    id=db.Column(db.Integer,primary_key=True)
    lastplayed_move=db.Column(db.String(255),nullable=False)
    player_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

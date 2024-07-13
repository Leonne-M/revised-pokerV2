from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config



db=SQLAlchemy()
migrate=Migrate()

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app,db)
    return app

app=create_app()

@app.route("/signup",methods=["POST"])
def create_user():
    from models import User
    body=request.get_json()
    name=body('name')
    email=body("email")
    password=body("password")
    user=User(name=name,email=email,password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()),201

@app.route('/login',methods=['POST'])
def login():
    from models import User
    email=request.form['email']
    password=request.form['password']
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error':'user not found'}), 400
    else:
        return jsonify({'message':'Success'}),201
    



if __name__=="__main__":
    app.run(debug=True)
    



    
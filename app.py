from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager,create_access_token
from flask_migrate import Migrate
from config import Config
from models import db

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    
    return app

app = create_app()

@app.route("/signup", methods=["POST"])
def create_user():
    from models import User  
    body = request.get_json()
    name = body['name']
    email = body['email']
    password = body['password']
    
    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Successful request"}), 201

@app.route("/login", methods=["POST"])
def login():
    body=request.get_json()
    email=body['email']
    password=body['password']
    from models import User

    user=User.query.filter_by(email=email).first()
    if user and user.password==password:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message":"error"})

if __name__ == "__main__":
    app.run(debug=True)




    
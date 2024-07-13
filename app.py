from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager,create_access_token
from flask_migrate import Migrate
from config import Config
from models import db

migrate = Migrate()
jwt=JWTManager()
bcrypt=Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    return app

app = create_app()

@app.route("/signup", methods=["POST"])
def create_user():
    from models import User  
    body = request.get_json()
    name = body['name']
    email = body['email']
    password = body['password']
    hashed_password=bcrypt.generate_password_hash(password).decode("utf-8")
    
    user = User(name=name, email=email, password=hashed_password)
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
    password_accept=bcrypt.check_password_hash(user.password.encode("utf-8"),password)
    if user and password_accept:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message":"Invalid credentials"})

if __name__ == "__main__":
    app.run(debug=True)




    
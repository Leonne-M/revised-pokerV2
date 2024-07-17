from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from flask_migrate import Migrate
from config import Config
from models import db,serialize_card
import random
import json

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
        access_token=create_access_token(identity={"id":user.id,"name":user.name})
        return jsonify({"message": "Login successful"},{"token":access_token}), 200
    else:
        return jsonify({"message":"Invalid credentials"})
@app.route("/trial", methods=["POST"])
@jwt_required()
def trial():
    from models import User
    current_user=get_jwt_identity()
    print(current_user)
    user=User.query.filter_by(id=current_user['id']).first()
    return {"message":f"Hello {user.name} You are authorized to access this endpoint."}


player_hand_ids=[]
computer_hand_ids=[]
@app.route("/add_cards", methods=["POST"])
def add_cards():
    from models import Card
    body=request.get_json
    suit=body['suit']
    rank=body['rank']
    image=body['image']
    new_card=Card(suits=suit,rank=rank,image=image)
    db.session.add(new_card)
    db.session.commit()
    return jsonify({"message": "Card added successfully"})

@app.route("/get_cards", methods=["GET"])
@jwt_required()
def get_cards():
    from models import Game
    from models import Card
    current_user = get_jwt_identity()
    deck=Card.query.all()
    random.shuffle(deck)
    player_hand=[]
    computer_hand=[]
    for i in range(4):
        player_hand.append(deck.pop())
        computer_hand.append(deck.pop())
    player_hand_ids = [card.id for card in player_hand]
    computer_hand_ids = [card.id for card in computer_hand]
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    newranks=['4', '5', '6', '7', '9', '10']
    newdeck=[(newrank,suit)for suit in suits for newrank in newranks]
    played=[random.choice(newdeck)]
    new_game = Game(
        lastplayed_move=played,
        player_id=current_user['id'],
        player_hand=player_hand_ids,
        computer_hand=computer_hand_ids
    )
    db.session.add(new_game)
    db.session.commit()
    
    return jsonify({
        "player_hand": [serialize_card(card) for card in player_hand],
        "computer_hand": [serialize_card(card) for card in computer_hand]
    })

@app.route("/player_moves", methods=["POST"])
@jwt_required()
def player_moves():
   from models import Card
   from models import Game
   deck=Card.query.all()
   random.shuffle(deck)
   body=request.get_json()
   id=body['id']
   rank=body['rank']
   suit=body['suit']
   current_user= get_jwt_identity()
   player_game=Game.query.filter_by(player_id=current_user["id"]).first()
   print (player_game)
   player_hands=[]
   new_id=[]
   new_player_hand=[]
   playercards_id=player_game.player_hand
   last_played=json.loads(player_game.lastplayed_move)
   print (type(last_played))
   print (last_played)
   print (last_played[0])
   print (last_played[1])
#    print (rank)
#    print (suit)
   if rank ==last_played[0] or suit==last_played[1]:
        player_game.player_hand = [card_id for card_id in playercards_id if card_id != id]
        player_game.lastplayed_move=(rank,suit)
        db.session.commit()
        for id in player_game.player_hand:
         player_hands.append(Card.query.filter_by(id=id).first())
        return jsonify({
            "message": "Successful move",
            "player_hand": [serialize_card(card) for card in player_hands]
        })
   if rank =="pick"and suit =="pick":
       for id in player_game.player_hand:
         player_hands.append(Card.query.filter_by(id=id).first())
         player_hands.append(deck.pop())
       for cards in player_hands:
                new_id.append(cards.id)
       player_game.player_hand=new_id
       db.session.commit()

       return jsonify({"player_hand": [serialize_card(card) for card in player_hands]})
   return jsonify([])

    
@app.route("/computer_moves",methods=["GET"])   
@jwt_required()
def computer_moves():
    from models import Game
    from models import Card
    current_user=get_jwt_identity()
    deck=Card.query.all()
    random.shuffle(deck)
    player_game=Game.query.filter_by(id=current_user.id).first()  
    computer_id=player_game.computer_hand
    computer_hand=[]
    playable=[]
    new_id=[]
    new_computer_hand=[]
    for id in computer_id:
        computer_hand.append(Card.query.filter_by(id=id).first())
    last_played=player_game.lastplayed_move
    for i in range(len(computer_hand)):
        if computer_hand[i]["rank"]==last_played[0] or computer_hand[i]["suit"]==last_played[1]:
            playable.append(computer_hand[i])
            playing=random.choice(playable)
            rank=playing['rank']
            suit=playing['suit']
            player_game.lastplayed_move=(rank,suit)
            player_game.computer_hand = [card_id for card_id in computer_id if card_id!= playing.id]
            db.session.commit()
            for id in player_game.computer_hand:
                new_computer_hand.append(Card.query.filter_by(id=id).first())
            return jsonify(new_computer_hand)
        if not playable:
            computer_hand.append(deck.pop())
            for cards in computer_hand:
                new_id.append(cards.id)
                player_game.computer_hand=new_id
                db.session.commit()
                return jsonify(computer_hand)

if __name__ == "__main__":
    app.run(debug=True)




    
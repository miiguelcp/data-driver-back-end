"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import Travel, db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['JWT_SECRET_KEY'] = os.environ.get('FLASK_APP_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET','POST'])
def handle_user():
    if request.method == 'GET':
        users = User.query.all()
        response = []
        for user in users:
            response.append(user.serialize())
        return jsonify(response), 200

    elif request.method == 'POST':
        body = request.json
        print(body)
        password = body['password'] 
        salt = os.urandom(8).hex()
        print(salt)
        body['salt'] = salt
        body['password'] = generate_password_hash(salt + password)
        create_user = User.create(body)
        if create_user is not None:
            return jsonify(create_user.serialize()), 201
        return jsonify({"Message": "User not created, try again"}), 400

@app.route('/user', methods=['PUT'])
@jwt_required()
def user_edit():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).one_or_none()
    if user is not None:
        updated = user.update(request.json)
        if updated:
            return jsonify(user.serialize()), 200
        else:
            return jsonify({"Message":"Something Happened, try again"}), 500
    return jsonify({"Message":"User Not Found"}), 404


@app.route('/perfil', methods=['GET'])
@jwt_required()
def handle_perfil():
    id = get_jwt_identity()
    user = User.query.filter_by(id=id).one_or_none()
    return jsonify(user.serialize()), 200


@app.route('/login', methods=['POST'])
def user_login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user_uno = User.query.filter_by(email=email).one_or_none()
    #user.email != "test@test.com" or user.password != "test"
    if user_uno is None:
        # No se encontro el usuario
        return jsonify({"msg": "Something went wrong, please try again!"}), 401
    salt = user_uno.salt
    # password_hasheado = generate_password_hash(password)
    if check_password_hash(user_uno.password, salt + password):
        access_token = create_access_token(identity=user_uno.id)
        return jsonify({ "token": access_token, "user_id": user_uno.id, "user_first_name": user_uno.first_name })
        print(user_id)
    return jsonify({"msg": "Invalid password!"}), 401

@app.route('/travel/<int:travel_id>', methods=['GET'])
@jwt_required ()

def handle_one_travel(travel_id):
    user_id = get_jwt_identity()
    #response = requests.get()
    travel = Travel.query.filter_by(id=travel_id).one_or_none()
    
    if travel is not None:
        return jsonify(travel.serialize()), 200
    else:
        return jsonify({"Message":"Travel Not Found"}), 400

@app.route('/travels', methods=['GET'])
@jwt_required()
def get_travel_user():

    user_id = get_jwt_identity()
    travels = Travel.query.filter_by(user_id=user_id)
    response = list(map(
        lambda travel: travel.serialize(),
        travels
    ))
    return jsonify(response), 200

@app.route('/details/<int:travel_id>', methods=['GET'])
@jwt_required()
def handle_details_travels(travel_id):
    body = request.json

@app.route('/travels', methods=['POST'])
@jwt_required()
def handle_users_travels():
    user_id = get_jwt_identity()
    initial_amount = request.json['initial_amount']
    lodging = request.json['lodging']
    food = request.json['food']
    fuel = request.json['fuel']
    toll = request.json['toll']
    unexpected = request.json['unexpected']
    new_travel = Travel(
        user_id=user_id,
        initial_amount= initial_amount,
        lodging= lodging,
        food= food,
        fuel= fuel,
        toll= toll,
        unexpected= unexpected,
    )
    db.session.add(new_travel)
    try:
        db.session.commit()
        return jsonify(new_travel.serialize()), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(error.args), 500



def handle_onee_travel(travel_id):
    #response = requests.get()
    travel = Travel.query.filter_by(id=travel_id).one_or_none()
    body = travel.json()
    if travel is not None:
        return jsonify(travel), 200
    else:
        return jsonify({"Message":"Travel Not Found"}), 400





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3500))
    app.run(host='0.0.0.0', port=PORT, debug=False)

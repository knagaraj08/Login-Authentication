import hashlib
import datetime

'''
Json Web Token {JWT}
JWT is basically a string that is encrypted on the server-side and holds information about the user,
when the user successfully login with their credentials
'''

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'by87u1f2clo8tylg2tfdf4'

jwt = JWTManager(app)

client = MongoClient("mongodb://localhost:27017")

db = client["Institution"]

user_collection = db["users"]


@app.route('/')
def hello():
    return "its Running"


# registering the user
@app.route('/api/v1/users', methods=['POST'])
def register():
    new_user = request.get_json()
    # let us encrypt the entered password for the security
    new_user["password"] = hashlib.sha256(new_user["password"].encode('utf-8')).hexdigest()

    # now first we will check if the user exits or not
    doc = user_collection.find_one({"username": new_user["username"]})
    if not doc:
        user_collection.insert_one(new_user)
        return jsonify({'message': 'User Created Successfully'}), 201
    else:
        return jsonify({'message': 'User already exists'}), 409
        # 409 - conflict error 


@app.route("/api/v1/login", methods=["POST"])
def login():
    login_details = request.get_json()
    # searching for the user here in the database
    user_from_db = user_collection.find_one({'username': login_details['username']})

    if user_from_db:
        encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrypted_password == user_from_db['password']:
            # now lets create a JWT token
            access_token = create_access_token(identity=user_from_db['username'])
            return jsonify(access_token=access_token), 200
            # return "Login Successful \n Welcome Back " + user_from_db['username']
    return jsonify({'message': 'The username or password is incorrect'}), 401


@app.route('/api/v1/get_user', methods=["GET"])
@jwt_required()
def profile():
    curr_user = get_jwt_identity()
    user_from_db = user_collection.find_one({"username": curr_user})

    if user_from_db:
        del user_from_db['_id'], user_from_db['password']
        return jsonify({"profile": user_from_db}), 200
    else:
        return jsonify({"message": "Profile Not Found"}), 404


if __name__ == '__main__':
    app.run(debug=True)

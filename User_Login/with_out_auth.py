from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017")
db = client["Dem"]
user_collection = db["users"]


@app.route('/')
def hello():
    return "its Running"


# registering the user
@app.route('/api/v1/users', methods=['POST'])
def register():
    new_user = request.get_json()
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
        encrypted_password = login_details['password']
        if encrypted_password == user_from_db['password']:
            return "Login Successful \n Welcome Back " + user_from_db['username']
    return jsonify({'message': 'The username or password is incorrect'}), 401


@app.route('/api/v1/get_user/<string:name>', methods=["GET"])
# @jwt_required()
def profile(name):
    cursor = user_collection.find({"username": name}, {"_id": 1, "username": 1})
    data = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)

from pymongo import MongoClient
from bson import ObjectId


client = MongoClient('localhost', 27017)
db = client['smartUser']
collection = db['users']

def register_user(user_data):
    if collection.find_one({'username': user_data['username']}):
        return {'error': 'Username already exists'}, 409
    collection.insert_one(user_data)
    return {'msg': 'User registered successfully'}, 201

def check_user(login_data):
    user = collection.find_one({'username': login_data['username'], 'password': login_data['password']})
    if user:
        return {'user_id': str(user['_id'])}, 200
    else:
        return {'error': 'Invalid username or password'}, 401

def get_user(user_id):
    user = collection.find_one({'_id': ObjectId(user_id)})
    if user:
        user_data = {key: user[key] for key in user if key not in ['_id', 'password']}
        return user_data, 200
    else:
        return {'error': 'User not found'}, 404

def update_user(user_id, update_data):
    result = collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
    if result.modified_count:
        return {'msg': 'User updated successfully'}, 200
    else:
        return {'error': 'Update failed'}, 400

def delete_user(user_id):
    result = collection.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count:
        return {'msg': 'User deleted successfully'}, 200
    else:
        return {'error': 'User not found'}, 404


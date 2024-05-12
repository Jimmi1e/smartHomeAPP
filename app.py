from flask import Flask, request, jsonify, session, redirect, url_for
import db_management

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/register', methods=['POST'])
def register():
    response, status = db_management.register_user(request.json)
    return jsonify(response), status

@app.route('/login', methods=['POST'])
def login():
    response, status = db_management.check_user(request.json)
    if status == 200:
        session['user_id'] = response['user_id']
    return jsonify(response), status

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return jsonify({'msg': 'Logged out'}), 200

@app.route('/user', methods=['GET'])
def get_user():
    if 'user_id' in session:
        response, status = db_management.get_user(session['user_id'])
    else:
        response, status = {'error': 'Not logged in'}, 401
    return jsonify(response), status

@app.route('/user/update', methods=['PUT'])
def update_user():
    if 'user_id' in session:
        response, status = db_management.update_user(session['user_id'], request.json)
    else:
        response, status = {'error': 'Not logged in'}, 401
    return jsonify(response), status

@app.route('/user/delete', methods=['DELETE'])
def delete_user():
    if 'user_id' in session:
        response, status = db_management.delete_user(session['user_id'])
        if status == 200:
            session.pop('user_id', None)
    else:
        response, status = {'error': 'Not logged in'}, 401
    return jsonify(response), status

if __name__ == '__main__':
    app.run(debug=True)

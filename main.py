from flask import Flask, request, jsonify
import jwt
import socket
import datetime
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '5cac4f980fedc3d3f1f99b4be3472c9b30d56523e632d151237ec9309048bda9'
app.config['REFRESH_SECRET_KEY'] = 'd6a5213ce6400efc7a95f284490870beabfad081a55b18b7d609165463492dcd'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.post("/login")
def login():
    Json = request.get_json()
    print(Json)
    auth = request.authorization

    if auth and auth.username == 'username' and auth.password == 'password':
        access_token = jwt.encode({'username': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'], algorithm='HS256')
        refresh_token = jwt.encode({'username': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['REFRESH_SECRET_KEY'], algorithm='HS256')
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token})
    
    return jsonify({'message': 'Invalid credentials!'}), 401

@app.post('/refresh')
def refresh():
    try:
        refresh_token = request.json.get('refresh_token')

        if not refresh_token:
            return jsonify({'message': 'Refresh token is missing!'}), 401

        data = jwt.decode(refresh_token, app.config['REFRESH_SECRET_KEY'], algorithms=['HS256'])
        new_access_token = jwt.encode({'username': data['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'access_token': new_access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token!'}), 401

@app.get('/protected')
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Welcome, {current_user}! This is a protected route.'})

@app.get("/")
def home():
    return "hello";

if __name__ == '__main__':
    app.debug=True
    IPAddr = socket.gethostbyname(socket.gethostname())  
    app.run(host=IPAddr, port=5000)
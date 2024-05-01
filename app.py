from flask import Flask, request, jsonify, make_response, render_template, session
import jwt, socket
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'de3b9e3f1a3d43a8ac7dc3474a7bd06a'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!' : 'Token is missing!'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert!' : 'Invalid Token!'})
    return decorated

@app.get('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Logged in currently'

@app.get('/public')
def public():
    return 'For public'

@app.get('/auth')
@token_required
def auth():
    return 'JWT is verified, Welcome to your Dashboard'

@app.post('/login')
def login():
    Json = request.get_json()
    print(Json)
    # if Json['username'] and Json['password'] == '123456':
    if request.form['username'] and request.form['password'] == '123456':
        session['logged_in'] = True
        token = jwt.encode({
            'user' : request.form['username'],
            'expiration' : str(datetime.utcnow() + timedelta(seconds=120))
        },
        app.config['SECRET_KEY'])
        return jsonify({'token' : token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate' : 'Basic realm:"Authentication Failed!"'})

if __name__ == "__main__":
    app.debug=True
    IPAddr = socket.gethostbyname(socket.gethostname())  
    app.run(host=IPAddr, port=5000)
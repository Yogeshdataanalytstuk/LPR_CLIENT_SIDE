from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from traceback import format_exc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, logger=True, engineio_logger=True)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class NumberPlate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and/or password.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    plates = NumberPlate.query.filter_by(user_id=current_user.id).order_by(NumberPlate.timestamp.desc()).limit(6).all()
    return render_template('dashboard.html', username=current_user.username, plates=plates)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@app.route('/force-logout', methods=['POST'])
def force_logout():
    logout_user()
    session.clear()
    return jsonify({'status': 'logged_out'}), 200


@app.route('/submit_plate', methods=['POST'])
@login_required
def submit_plate():
    try:
        data = request.json
        plate = data.get('plate')
        if plate:
            number_plate = NumberPlate(plate=plate, user_id=current_user.id)
            db.session.add(number_plate)
            db.session.commit()
            plates = NumberPlate.query.filter_by(user_id=current_user.id).order_by(NumberPlate.timestamp.desc()).limit(6).all()
            plates_data = [{'plate': p.plate, 'timestamp': p.timestamp.isoformat()} for p in plates]
            socketio.emit('update_plates', plates_data)
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'failure', 'message': 'No plate data provided'}), 400
    except Exception as e:
        app.logger.error("Error processing the request:")
        app.logger.error(format_exc())
        return jsonify({'status': 'failure', 'message': str(e)}), 500


@socketio.on('connect')
def test_connect():
    if current_user.is_authenticated:
        print(f'Client {current_user.username} connected')

@socketio.on('disconnect')
def test_disconnect():
    if current_user.is_authenticated:
        print(f'Client {current_user.username} disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)

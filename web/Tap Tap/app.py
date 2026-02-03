import os
import psycopg2
import psycopg2.extras
from psycopg2 import errors
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

FLAG = 'RCSC{Tap_Tap_is_fun}'
COST_TO_BUY_FLAG = 586

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')


def get_db_conn():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            dbname=os.environ.get('POSTGRES_DB', 'ctfdb'),
            user=os.environ.get('POSTGRES_USER', 'ctf'),
            password=os.environ.get('POSTGRES_PASSWORD', 'ctfpass'),
            port=int(os.environ.get('POSTGRES_PORT', '5432')),
        )
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def init_db():
    db = get_db_conn()
    with db.cursor() as cur:
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS users (
                   id SERIAL PRIMARY KEY,
                   username TEXT UNIQUE NOT NULL,
                   password_hash TEXT NOT NULL,
                   points INTEGER NOT NULL DEFAULT 0,
                   has_flag BOOLEAN NOT NULL DEFAULT FALSE
               )'''
        )
    db.commit()


@app.before_request
def ensure_db():
    # Ensure schema exists; cheap no-op after first time
    try:
        init_db()
    except Exception:
        # If DB is not ready yet, let the request fail naturally
        pass


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    db = get_db_conn()
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute('SELECT * FROM users WHERE id = %s', (uid,))
        user = cur.fetchone()
    return user


def login_required(view_func):
    def wrapper(*args, **kwargs):
        if not current_user():
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@app.route('/')
def index():
    if current_user():
        return redirect(url_for('game'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            return render_template('register.html', error='Username and password are required.')
        pw_hash = generate_password_hash(password)
        db = get_db_conn()
        try:
            with db.cursor() as cur:
                cur.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, pw_hash))
            db.commit()
        except errors.UniqueViolation:
            db.rollback()
            return render_template('register.html', error='Username already taken.')
        except Exception:
            db.rollback()
            return render_template('register.html', error='Registration failed. Try a different username.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db_conn()
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cur.fetchone()
        if not user or not check_password_hash(user['password_hash'], password):
            return render_template('login.html', error='Invalid credentials.')
        session['user_id'] = user['id']
        return redirect(url_for('game'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/game')
@login_required
def game():
    user = current_user()
    return render_template('game.html', points=user['points'], has_flag=bool(user['has_flag']), cost=COST_TO_BUY_FLAG)


@app.route('/api/status')
@login_required
def api_status():
    user = current_user()
    return jsonify({
        'points': user['points'],
        'has_flag': bool(user['has_flag']),
        'cost': COST_TO_BUY_FLAG
    })


@app.route('/api/click', methods=['POST'])
@login_required
def api_click():
    user = current_user()
    db = get_db_conn()
    try:
        data = request.get_json(silent=True) or {}
        # Vulnerable trust of client-provided gain parameter (intended for the challenge)
        gain = int(data.get('gain', 1))
    except (ValueError, TypeError):
        gain = 1

    # Bound a bit to avoid overflow but still allow the intended 700 exploit
    if gain < 0:
        gain = 0
    if gain > 1000000:
        gain = 1000000

    with db.cursor() as cur:
        cur.execute('UPDATE users SET points = points + %s WHERE id = %s', (gain, user['id']))
    db.commit()
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute('SELECT points FROM users WHERE id = %s', (user['id'],))
        new_points = cur.fetchone()['points']
    return jsonify({'ok': True, 'points': new_points})


@app.route('/api/buy', methods=['POST'])
@login_required
def api_buy():
    user = current_user()
    if user['has_flag']:
        return jsonify({'ok': True, 'message': 'Already purchased.', 'flag': FLAG})

    if user['points'] < COST_TO_BUY_FLAG:
        return jsonify({'ok': False, 'error': 'Not enough points.'}), 400

    db = get_db_conn()
    with db.cursor() as cur:
        cur.execute('UPDATE users SET points = points - %s, has_flag = TRUE WHERE id = %s', (COST_TO_BUY_FLAG, user['id']))
    db.commit()

    return jsonify({'ok': True, 'flag': FLAG})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

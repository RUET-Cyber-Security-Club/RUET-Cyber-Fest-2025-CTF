import os
import sqlite3
import secrets
import random
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
from werkzeug.security import generate_password_hash, check_password_hash

# --- App & Config ---

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists for SQLite
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-' + secrets.token_hex(16)),
        'DATABASE': os.path.join(app.instance_path, 'rcsc.db'),
        'FLAG': os.environ.get('FLAG', 'RCSC{4dm1n_Tells_just_t0_b3_easy}'),
    })

    # DB helpers
    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.executescript(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                code TEXT,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            '''
        )
        db.commit()

    def seed_admin_and_posts():
        db = get_db()
        cur = db.execute('SELECT COUNT(*) AS c FROM users')
        count = cur.fetchone()['c']
        if count == 0:
            # Create admin first so it gets id=1
            admin_user = 'Administrator'
            # Strong password (unknown to players)
            admin_pass = os.environ.get('ADMIN_PASSWORD', 'Adm1n!2025$RCSC_' + secrets.token_hex(4))
            db.execute(
                'INSERT INTO users (username, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?)',
                (admin_user, generate_password_hash(admin_pass), 1, datetime.utcnow().isoformat())
            )
            # Seed a normal demo user (optional)
            db.execute(
                'INSERT INTO users (username, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?)',
                ('player', generate_password_hash('player123'), 0, datetime.utcnow().isoformat())
            )
            # Seed posts
            posts = [
                ('Welcome to RCSC Cyber Fest 2025',
                 'Get ready for challenges, workshops, and talks on cybersecurity!'),
                ('Previous Highlights',
                 'From CTF finals to expert panels—recap of 2023–2024 events.'),
                ('Achievements',
                 'Celebrating teams who solved the toughest exploits and puzzles.'),
            ]
            for t, c in posts:
                db.execute(
                    'INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)',
                    (t, c, datetime.utcnow().isoformat())
                )
            db.commit()
            print('Admin seeded with username=Administrator and a strong password (hidden).')

    def login_required(view):
        def wrapped(*args, **kwargs):
            if not session.get('user_id'):
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        wrapped.__name__ = view.__name__
        return wrapped

    def current_user():
        if not session.get('user_id'):
            return None
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        return user

    # Utility to generate a 6-digit code
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

    # Routes
    @app.route('/')
    def index():
        if session.get('user_id'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        db = get_db()
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            if not username or not password:
                flash('Username and password are required.', 'danger')
                return render_template('register.html')
            existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                flash('Username already exists.', 'danger')
                return render_template('register.html')
            db.execute(
                'INSERT INTO users (username, password_hash, is_admin, created_at) VALUES (?, ?, 0, ?)',
                (username, generate_password_hash(password), datetime.utcnow().isoformat())
            )
            db.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        db = get_db()
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = bool(user['is_admin'])
                flash('Logged in successfully.', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid credentials.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        db = get_db()
        posts = db.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
        return render_template('dashboard.html', posts=posts)

    @app.route('/posts')
    @login_required
    def posts():
        db = get_db()
        posts = db.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
        return render_template('posts.html', posts=posts)

    @app.route('/notifications')
    @login_required
    def notifications():
        db = get_db()
        user = current_user()
        notes = db.execute(
            'SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC',
            (user['id'],)
        ).fetchall()
        return render_template('notifications.html', notes=notes)

    @app.route('/profile', methods=['GET'])
    @login_required
    def profile():
        user = current_user()
        return render_template('profile.html', user=user)

    @app.route('/profile/send_code', methods=['POST'])
    @login_required
    def send_code():
        db = get_db()
        user = current_user()
        code = generate_code()
        message = f"Your password change code is: {code}"
        db.execute(
            'INSERT INTO notifications (user_id, message, code, used, created_at) VALUES (?, ?, ?, 0, ?)',
            (user['id'], message, code, datetime.utcnow().isoformat())
        )
        db.commit()
        flash('Verification code sent to your notifications.', 'info')
        return redirect(url_for('profile'))

    # Vulnerable password change endpoint (IDOR)
    @app.route('/profile/change_password', methods=['POST'])
    @login_required
    def change_password():
        db = get_db()
        user = current_user()

        new_password = request.form.get('new_password', '').strip()
        code = request.form.get('code', '').strip()

        # Accept id from form or querystring (vulnerability vector remains)
        target_id = request.form.get('id') or request.args.get('id') or str(user['id'])

        # Validate code: must exist and be unused (can be used by anyone)
        code_row = db.execute(
            'SELECT * FROM notifications WHERE code = ? AND used = 0',
            (code,)
        ).fetchone()
        if not code_row:
            flash('Invalid or used code.', 'danger')
            return redirect(url_for('profile'))

        if not new_password:
            flash('New password required.', 'danger')
            return redirect(url_for('profile'))

        # Apply password change to target_id (IDOR)
        db.execute(
            'UPDATE users SET password_hash = ? WHERE id = ?',
            (generate_password_hash(new_password), int(target_id))
        )
        # Single-use: delete the code row entirely so it cannot be reused
        db.execute('DELETE FROM notifications WHERE id = ?', (code_row['id'],))
        db.commit()

        flash('Password changed successfully.', 'success')
        return redirect(url_for('profile'))

    @app.route('/admin')
    @login_required
    def admin():
        if not session.get('is_admin'):
            abort(403)
        flag = create_app._app_ctx_stack.top.app.config['FLAG'] if hasattr(create_app, '_app_ctx_stack') else app.config['FLAG']
        # Simpler access
        flag = app.config['FLAG']
        return render_template('admin.html', flag=flag)

    # Initialize DB on first run
    with app.app_context():
        init_db()
        seed_admin_and_posts()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

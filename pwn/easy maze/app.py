#!/usr/bin/env python3
import os
import sqlite3
import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, g, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

# ===================== CONFIG =====================

APP_DIR = os.path.dirname(__file__)        # /app inside container
DATA_DIR = os.path.join(APP_DIR, "data")   # /app/data
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE = os.path.join(DATA_DIR, "maze.db")

SECRET_KEY = os.environ.get("SECRET_KEY", "change_me_in_real_ctf")
FLAG = os.environ.get("MAZE_FLAG", "RCSC{W4lk_Th3_L0ng_M4z3}")

GAME_TIME_LIMIT_SECONDS = 40   # total time limit per run
IDLE_AUTO_MOVE_SECONDS = 0     # auto-move disabled


# ===================== MAZE LOADING =====================

def load_maze():
    path = os.path.join(APP_DIR, "map.txt")
    with open(path, "r") as f:
        lines = [line.rstrip("\n") for line in f.readlines() if line.strip()]
    if not lines:
        raise RuntimeError("map.txt is empty")
    width = len(lines[0])
    for line in lines:
        if len(line) != width:
            raise RuntimeError("All lines in map.txt must be the same length")
    return lines

MAZE = load_maze()
ROWS = len(MAZE)
COLS = len(MAZE[0])


# ===================== FLASK APP =====================

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # set True behind HTTPS
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(hours=12)


# ===================== DB HELPERS =====================

def init_db():
    """Create DB tables if not exist (no app context needed)."""
    conn = sqlite3.connect(DATABASE)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                flag_unlocked INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                move_char TEXT NOT NULL,
                is_auto INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS game_state (
                user_id INTEGER PRIMARY KEY,
                row_pos INTEGER NOT NULL,
                col_pos INTEGER NOT NULL,
                game_start TEXT NOT NULL,
                finished INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()

        # Try to add flag_unlocked column if missing (safe if already exists)
        try:
            conn.execute(
                "ALTER TABLE users ADD COLUMN flag_unlocked "
                "INTEGER NOT NULL DEFAULT 0"
            )
            conn.commit()
        except Exception:
            pass

    finally:
        conn.close()


# Initialize DB at import time
init_db()


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ===================== AUTH HELPERS =====================

def get_current_user():
    """Return current user row or None. DO NOT clear session here."""
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE id = ?", (uid,))
    return cur.fetchone()


def login_required(f):
    """Simple check: only require that user_id is in session."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_current_user():
    """Make current_user available in templates."""
    user = get_current_user()
    return {"current_user": user}


# ===================== MAZE / GAME HELPERS =====================

def find_start():
    for r in range(ROWS):
        for c in range(COLS):
            if MAZE[r][c] == "S":
                return r, c
    raise RuntimeError("No 'S' start position found in map.txt")


def get_cell(r, c):
    if 0 <= r < ROWS and 0 <= c < COLS:
        return MAZE[r][c]
    return "#"  # outside is wall


def reset_game_for_user(user_id):
    """Reset maze state in DB for a user."""
    sr, sc = find_start()
    now = datetime.datetime.utcnow().isoformat()
    db = get_db()
    db.execute(
        """
        INSERT INTO game_state (user_id, row_pos, col_pos, game_start, finished)
        VALUES (?, ?, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            row_pos = excluded.row_pos,
            col_pos = excluded.col_pos,
            game_start = excluded.game_start,
            finished = 0
        """,
        (user_id, sr, sc, now),
    )
    db.commit()


def get_persistent_flag_status(user_id):
    """Check DB if flag unlocked for this user."""
    db = get_db()
    cur = db.execute(
        "SELECT flag_unlocked FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    if not row:
        return False
    return bool(row["flag_unlocked"])


def get_game_state_for_user(user_id):
    """Return current game state for a user, computed from DB."""
    db = get_db()
    cur = db.execute(
        "SELECT row_pos, col_pos, game_start, finished FROM game_state WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()

    if not row:
        reset_game_for_user(user_id)
        cur = db.execute(
            "SELECT row_pos, col_pos, game_start, finished FROM game_state WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()

    game_start = datetime.datetime.fromisoformat(row["game_start"])
    now = datetime.datetime.utcnow()
    elapsed = (now - game_start).total_seconds()
    remaining = max(0, GAME_TIME_LIMIT_SECONDS - int(elapsed))

    finished = bool(row["finished"])

    # If time is up and not finished, reset but stay logged in
    if remaining <= 0 and not finished:
        reset_game_for_user(user_id)
        cur = db.execute(
            "SELECT row_pos, col_pos, game_start, finished FROM game_state WHERE user_id = ?",
            (user_id,),
        )
        row = cur.fetchone()
        game_start = datetime.datetime.fromisoformat(row["game_start"])
        now = datetime.datetime.utcnow()
        elapsed = (now - game_start).total_seconds()
        remaining = max(0, GAME_TIME_LIMIT_SECONDS - int(elapsed))
        finished = bool(row["finished"])

    return {
        "row": row["row_pos"],
        "col": row["col_pos"],
        "remaining_seconds": remaining,
        "finished": finished,
        "flag_unlocked": get_persistent_flag_status(user_id),
    }


def update_game_state(user_id, row_pos, col_pos, finished=None):
    db = get_db()
    if finished is None:
        db.execute(
            """
            UPDATE game_state
            SET row_pos = ?, col_pos = ?
            WHERE user_id = ?
            """,
            (row_pos, col_pos, user_id),
        )
    else:
        db.execute(
            """
            UPDATE game_state
            SET row_pos = ?, col_pos = ?, finished = ?
            WHERE user_id = ?
            """,
            (row_pos, col_pos, 1 if finished else 0, user_id),
        )
    db.commit()


def log_move(user_id, move_char, is_auto=False):
    db = get_db()
    db.execute(
        "INSERT INTO moves (user_id, move_char, is_auto) VALUES (?, ?, ?)",
        (user_id, move_char, 1 if is_auto else 0),
    )
    db.commit()


def apply_move(user_id, move_char, is_auto=False):
    state = get_game_state_for_user(user_id)

    # Time check only on backend
    if state["remaining_seconds"] <= 0:
        reset_game_for_user(user_id)
        flash("Game Over! Time is up. Maze restarted.", "danger")
        return

    deltas = {
        "w": (-1, 0),
        "s": (1, 0),
        "a": (0, -1),
        "d": (0, 1),
    }
    if move_char not in deltas:
        return

    dr, dc = deltas[move_char]
    nr = state["row"] + dr
    nc = state["col"] + dc
    cell = get_cell(nr, nc)

    # Wall hit => reset maze
    if cell == "#":
        reset_game_for_user(user_id)
        log_move(user_id, move_char, is_auto=is_auto)
        return

    # Valid move
    update_game_state(user_id, nr, nc, finished=state["finished"])
    log_move(user_id, move_char, is_auto=is_auto)

    # Reached finish
    if cell == "F":
        update_game_state(user_id, nr, nc, finished=True)
        db = get_db()
        db.execute(
            "UPDATE users SET flag_unlocked = 1 WHERE id = ?",
            (user_id,),
        )
        db.commit()
        flash("You reached the exit! Flag unlocked.", "success")


# ===================== ROUTES =====================

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("game"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password required.", "danger")
            return render_template("register.html")

        db = get_db()
        cur = db.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            flash("Username already exists.", "danger")
            return render_template("register.html")

        pw_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, pw_hash),
        )
        db.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            reset_game_for_user(user["id"])
            flash("Logged in.", "success")
            return redirect(url_for("game"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/game")
@login_required
def game():
    uid = session["user_id"]
    user = get_current_user()  # may be None if DB was reset; handle in template
    state = get_game_state_for_user(uid)

    # Build grid with moving player
    grid = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            cell = MAZE[r][c]
            if r == state["row"] and c == state["col"]:
                row.append("*")  # player marker
            else:
                row.append(cell)
        grid.append(row)

    flag_value = FLAG if state["flag_unlocked"] else None

    return render_template(
        "game.html",
        user=user,
        grid=grid,
        remaining_seconds=state["remaining_seconds"],
        flag=flag_value,
        idle_auto_move_seconds=IDLE_AUTO_MOVE_SECONDS,
    )


@app.route("/move", methods=["POST"])
@login_required
def move():
    direction = request.form.get("direction", "")
    uid = session["user_id"]
    apply_move(uid, direction, is_auto=False)
    return redirect(url_for("game"))


@app.route("/state")
@login_required
def state():
    uid = session["user_id"]
    return jsonify(get_game_state_for_user(uid))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

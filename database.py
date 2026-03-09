import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "quiz_web.db"

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    return sqlite3.connect(db_path)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            avatar TEXT DEFAULT 'default.png',
            theme TEXT DEFAULT 'dark'
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL DEFAULT 'General',
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL
        )
    ''')
    
    # Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            incorrect_answers INTEGER NOT NULL,
            time_spent INTEGER NOT NULL, -- in seconds
            date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Try creating a default admin if none exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ("admin",))
    if not cursor.fetchone():
        hashed = generate_password_hash("admin")
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hashed, "admin"))

    # Try creating a default user if none exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ("user",))
    if not cursor.fetchone():
        hashed = generate_password_hash("password")
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("user", hashed, "user"))
        
    conn.commit()
    conn.close()

# User Operations
def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, role, theme FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row and check_password_hash(row[1], password):
        return {"id": row[0], "username": username, "role": row[2], "theme": row[3]}
    return None

def update_user_password(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
    conn.commit()
    conn.close()

def update_user_theme(user_id, theme):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
    conn.commit()
    conn.close()

# Question Operations
def add_question(category, text, a, b, c, d, correct):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (category, question_text, option_a, option_b, option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, text, a, b, c, d, correct))
    conn.commit()
    conn.close()

def get_all_questions():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions

def delete_question(question_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()

def get_questions_category_distribution():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT category, COUNT(*) FROM questions GROUP BY category')
    data = cursor.fetchall()
    conn.close()
    return data

# Results Operations
def save_result(user_id, score, total, correct, incorrect, time_spent):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO results (user_id, score, total_questions, correct_answers, incorrect_answers, time_spent)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, score, total, correct, incorrect, time_spent))
    conn.commit()
    conn.close()

def get_user_results(user_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM results WHERE user_id = ? ORDER BY date_taken DESC', (user_id,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def get_all_results_with_users():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, u.username 
        FROM results r 
        JOIN users u ON r.user_id = u.id 
        ORDER BY r.date_taken DESC
    ''')
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

if __name__ == "__main__":
    initialize_db()
    print("Web DB Initialized")

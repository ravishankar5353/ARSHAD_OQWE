import sqlite3
import os

DB_NAME = "quiz.db"

def get_connection():
    # Make sure DB is created in the same directory as this script
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    return sqlite3.connect(db_path)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL
        )
    ''')
    
    # Create results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_question(text, a, b, c, d, correct):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (text, a, b, c, d, correct))
    conn.commit()
    conn.close()

def get_all_questions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    questions = cursor.fetchall()
    conn.close()
    return questions

def delete_question(question_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()

def save_result(student_name, score, total):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (student_name, score, total_questions) VALUES (?, ?, ?)',
                   (student_name, score, total))
    conn.commit()
    conn.close()

def get_all_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM results ORDER BY date_taken DESC')
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    initialize_db()
    print("Database initialized.")

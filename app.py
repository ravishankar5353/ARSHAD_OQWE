from flask import Flask, render_template, request, redirect, url_session, session, jsonify, flash
import database
import os

app = Flask(__name__)
app.secret_key = 'super_secret_glass_key'

# Initialize DB on start
with app.app_context():
    database.initialize_db()

# --- Middleware ---
def login_required(role=None):
    def wrapper(func):
        def inner(*args, **kwargs):
            if 'user_id' not in session:
                return redirect('/login')
            if role and session.get('role') != role:
                return redirect('/dashboard')
            return func(*args, **kwargs)
        inner.__name__ = func.__name__
        return inner
    return wrapper

# --- Base Routes ---
@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = database.verify_user(request.form.get('username'), request.form.get('password'))
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['theme'] = user['theme']
            
            if user['role'] == 'admin':
                return redirect('/admin')
            return redirect('/dashboard')
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- Admin Routes ---
@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    questions = database.get_all_questions()
    results = database.get_all_results_with_users()
    cat_dist = database.get_questions_category_distribution()
    return render_template('admin_dashboard.html', questions=questions, results=results, cat_dist=cat_dist)

@app.route('/admin/question/add', methods=['POST'])
@login_required(role='admin')
def admin_add_question():
    data = request.form
    database.add_question(
        data.get('category', 'General'),
        data.get('question_text'),
        data.get('option_a'),
        data.get('option_b'),
        data.get('option_c'),
        data.get('option_d'),
        data.get('correct_option')
    )
    flash('Question added successfully.', 'success')
    return redirect('/admin')

@app.route('/admin/question/delete/<int:q_id>')
@login_required(role='admin')
def admin_delete_question(q_id):
    database.delete_question(q_id)
    flash('Question deleted.', 'success')
    return redirect('/admin')

# --- User Routes ---
@app.route('/dashboard')
@login_required(role='user')
def user_dashboard():
    results = database.get_user_results(session['user_id'])
    return render_template('user_dashboard.html', results=results)

@app.route('/quiz')
@login_required(role='user')
def quiz():
    questions = database.get_all_questions()
    if not questions:
        flash("No questions available.", "error")
        return redirect('/dashboard')
    # Can pick random or sequential. Passing all to JS for simplicity.
    return render_template('quiz.html', questions=questions)

@app.route('/quiz/submit', methods=['POST'])
@login_required(role='user')
def submit_quiz():
    data = request.json
    score = data.get('score', 0)
    total = data.get('total', 0)
    correct = data.get('correct', 0)
    incorrect = data.get('incorrect', 0)
    time_spent = data.get('time_spent', 0)
    
    database.save_result(session['user_id'], score, total, correct, incorrect, time_spent)
    return jsonify({"status": "success"})

@app.route('/reports')
@login_required(role='user')
def reports():
    results = database.get_user_results(session['user_id'])
    
    if not results:
        flash("No reports available yet. Take a quiz!", "error")
        return redirect('/dashboard')
        
    latest = results[0]
    return render_template('reports.html', latest=latest, all_results=results)

@app.route('/settings', methods=['GET', 'POST'])
@login_required()
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'theme':
            theme = request.form.get('theme')
            database.update_user_theme(session['user_id'], theme)
            session['theme'] = theme
            flash('Theme updated!', 'success')
        elif action == 'password':
            pwd = request.form.get('password')
            if pwd:
                database.update_user_password(session['user_id'], pwd)
                flash('Password updated!', 'success')
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

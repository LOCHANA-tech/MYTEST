from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL', 'https://yckxqefpsersuarvewvl.supabase.co')
supabase_key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlja3hxZWZwc2Vyc3VhcnZld3ZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4MjExNjIsImV4cCI6MjA3MzM5NzE2Mn0.Yz5hlqCLFqPIKVMTWnlYw68bA_LfjV2vK_Xw5O6nXY4')

supabase: Client = create_client(supabase_url, supabase_key)

# Hardcoded credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# API endpoints for student CRUD operations
@app.route('/api/students', methods=['GET'])
@login_required
def get_students():
    try:
        response = supabase.table('students').select('*').execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['POST'])
@login_required
def create_student():
    try:
        data = request.json
        name = data.get('name')
        age = data.get('age')
        
        if not name or not age:
            return jsonify({'error': 'Name and age are required'}), 400
        
        response = supabase.table('students').insert({'name': name, 'age': age}).execute()
        return jsonify(response.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
@login_required
def update_student(student_id):
    try:
        data = request.json
        name = data.get('name')
        age = data.get('age')
        
        if not name or not age:
            return jsonify({'error': 'Name and age are required'}), 400
        
        response = supabase.table('students').update({'name': name, 'age': age}).eq('id', student_id).execute()
        return jsonify(response.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    try:
        response = supabase.table('students').delete().eq('id', student_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)

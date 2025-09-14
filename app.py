from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Supabase configuration
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Authentication credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'

def is_authenticated():
    """Check if user is authenticated"""
    return 'logged_in' in session and session['logged_in']

def get_students():
    """Get all students from Supabase"""
    try:
        response = supabase.table('students').select('*').execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        return []

def add_student(name, age):
    """Add a new student to Supabase"""
    try:
        response = supabase.table('students').insert({'name': name, 'age': age}).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        return None

def update_student(student_id, name, age):
    """Update student in Supabase"""
    try:
        response = supabase.table('students').update({'name': name, 'age': age}).eq('id', student_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error updating student: {e}")
        return None

def delete_student(student_id):
    """Delete student from Supabase"""
    try:
        response = supabase.table('students').delete().eq('id', student_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Main route - redirect to login or dashboard based on auth"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
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

@app.route('/dashboard')
def dashboard():
    """Main dashboard (requires authentication)"""
    if not is_authenticated():
        return redirect(url_for('login'))
    
    students = get_students()
    return render_template('dashboard.html', students=students)

@app.route('/logout')
def logout():
    """Clear session and redirect to login"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# API Routes for CRUD operations
@app.route('/api/students', methods=['GET'])
def api_get_students():
    """Get all students"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    students = get_students()
    return jsonify(students)

@app.route('/api/students', methods=['POST'])
def api_add_student():
    """Add a new student"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    
    if not name or not age:
        return jsonify({'error': 'Name and age are required'}), 400
    
    result = add_student(name, age)
    if result:
        return jsonify({'message': 'Student added successfully', 'student': result[0]}), 201
    else:
        return jsonify({'error': 'Failed to add student'}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def api_update_student(student_id):
    """Update a student"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    
    if not name or not age:
        return jsonify({'error': 'Name and age are required'}), 400
    
    result = update_student(student_id, name, age)
    if result:
        return jsonify({'message': 'Student updated successfully', 'student': result[0]}), 200
    else:
        return jsonify({'error': 'Failed to update student'}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def api_delete_student(student_id):
    """Delete a student"""
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    result = delete_student(student_id)
    if result:
        return jsonify({'message': 'Student deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete student'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)

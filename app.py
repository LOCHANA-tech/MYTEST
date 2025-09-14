from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import logging
from functools import wraps

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    logger.error("Supabase URL or key not found in environment variables")
    raise ValueError("Supabase configuration not found")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    raise

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
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
        
        # Hardcoded authentication
        if username == 'admin' and password == '123':
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    logger.info("User logged out")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Fetch students from Supabase
        response = supabase.table('students').select('*').order('id', desc=False).execute()
        
        if response.data:
            students = response.data
            logger.info(f"Retrieved {len(students)} students from database")
        else:
            students = []
            logger.warning("No students found in database")
            
        return render_template('dashboard.html', students=students)
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        flash('Error loading student data', 'error')
        return render_template('dashboard.html', students=[])

# Student CRUD operations
@app.route('/students', methods=['POST'])
@login_required
def create_student():
    try:
        name = request.form.get('name')
        age = request.form.get('age')
        
        if not name or not age:
            flash('Name and age are required', 'error')
            return redirect(url_for('dashboard'))
        
        age = int(age)
        if age <= 0:
            flash('Age must be a positive number', 'error')
            return redirect(url_for('dashboard'))
        
        response = supabase.table('students').insert({
            'name': name,
            'age': age
        }).execute()
        
        if response.data:
            flash('Student added successfully!', 'success')
            logger.info(f"Added new student: {name}, age {age}")
        else:
            flash('Error adding student', 'error')
            logger.error("Failed to add student to database")
            
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        flash('Error adding student', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/students/<int:student_id>', methods=['PUT'])
@login_required
def update_student(student_id):
    try:
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        
        if not name or not age:
            return jsonify({'error': 'Name and age are required'}), 400
        
        age = int(age)
        if age <= 0:
            return jsonify({'error': 'Age must be a positive number'}), 400
        
        response = supabase.table('students').update({
            'name': name,
            'age': age
        }).eq('id', student_id).execute()
        
        if response.data:
            logger.info(f"Updated student {student_id}: {name}, age {age}")
            return jsonify({'message': 'Student updated successfully', 'student': response.data[0]})
        else:
            logger.error(f"Failed to update student {student_id}")
            return jsonify({'error': 'Failed to update student'}), 400
            
    except Exception as e:
        logger.error(f"Error updating student {student_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/students/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    try:
        response = supabase.table('students').delete().eq('id', student_id).execute()
        
        if response.data:
            logger.info(f"Deleted student {student_id}")
            return jsonify({'message': 'Student deleted successfully'})
        else:
            logger.error(f"Failed to delete student {student_id}")
            return jsonify({'error': 'Failed to delete student'}), 400
            
    except Exception as e:
        logger.error(f"Error deleting student {student_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/students')
@login_required
def get_students_api():
    try:
        response = supabase.table('students').select('*').order('id', desc=False).execute()
        
        if response.data:
            return jsonify({'students': response.data})
        else:
            return jsonify({'students': []})
            
    except Exception as e:
        logger.error(f"Error fetching students API: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return no content

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', message='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

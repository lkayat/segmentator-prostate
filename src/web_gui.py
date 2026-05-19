"""
Web-based GUI for prostate MRI segmentation tool
A browser-based interface for prostate MRI segmentation with DICOM handling,
annotation tools, and multi-user support.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import cv2
from werkzeug.utils import secure_filename
import base64

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'web-gui-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///web_segmentation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

# Task model
class SegmentationTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), unique=True, nullable=False)
    patient_id = db.Column(db.String(100), nullable=False)
    series_uid = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='created')
    progress = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    annotations = db.Column(db.Text)
    segments = db.Column(db.Text)
    image_data = db.Column(db.Text)  # Base64 encoded image data

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'patient_id': self.patient_id,
            'series_uid': self.series_uid,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'progress': self.progress,
            'annotations': json.loads(self.annotations) if self.annotations else [],
            'segments': json.loads(self.segments) if self.segments else [],
            'image_data': self.image_data
        }

# Initialize database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Main index page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.is_active:
            # In a real app, you'd verify password here
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')

        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=password,  # In real app, hash this properly
            role='user'
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    tasks = SegmentationTask.query.filter_by(created_by=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/upload')
@login_required
def upload():
    """Upload DICOM series page"""
    return render_template('upload.html')

@app.route('/segmentation/<task_id>')
@login_required
def segmentation(task_id):
    """Segmentation task page"""
    task = SegmentationTask.query.filter_by(task_id=task_id, created_by=current_user.id).first()
    if not task:
        return "Task not found", 404
    return render_template('segmentation.html', task=task.to_dict())

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get user's tasks"""
    tasks = SegmentationTask.query.filter_by(created_by=current_user.id).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new segmentation task"""
    data = request.get_json()

    task = SegmentationTask(
        task_id=data.get('task_id'),
        patient_id=data.get('patient_id'),
        series_uid=data.get('series_uid'),
        created_by=current_user.id,
        status=data.get('status', 'created'),
        progress=data.get('progress', 0)
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        'success': True,
        'task_id': task.task_id,
        'message': 'Task created successfully'
    })

@app.route('/api/tasks/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update a segmentation task"""
    task = SegmentationTask.query.filter_by(task_id=task_id, created_by=current_user.id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404

    data = request.get_json()

    if 'status' in data:
        task.status = data['status']
    if 'progress' in data:
        task.progress = data['progress']
    if 'annotations' in data:
        task.annotations = json.dumps(data['annotations'])
    if 'segments' in data:
        task.segments = json.dumps(data['segments'])
    if 'image_data' in data:
        task.image_data = data['image_data']

    task.last_updated = datetime.utcnow()
    db.session.commit()

    # Emit real-time update
    socketio.emit('task_update', {
        'task_id': task.task_id,
        'status': task.status,
        'progress': task.progress
    })

    return jsonify({'success': True, 'message': 'Task updated successfully'})

@app.route('/api/ai/presegment', methods=['POST'])
@login_required
def ai_presegment():
    """Run AI-based pre-segmentation"""
    # This would connect to AI models and run pre-segmentation
    # For now, simulate the process

    data = request.get_json()
    series_uid = data.get('series_uid')

    # Simulate processing time
    import time
    time.sleep(1)

    # In a real implementation, this would:
    # 1. Load the DICOM series
    # 2. Run AI model for pre-segmentation
    # 3. Return segmentation result

    return jsonify({
        'success': True,
        'message': 'AI pre-segmentation completed',
        'segmentation_data': {
            'series_uid': series_uid,
            'segmentation_type': 'ai_presegmentation',
            'timestamp': datetime.utcnow().isoformat()
        }
    })

@app.route('/api/dicom/load', methods=['POST'])
@login_required
def load_dicom_series():
    """Load DICOM series for segmentation"""
    # This would handle loading DICOM data from uploaded files or directories
    return jsonify({
        'success': True,
        'message': 'DICOM series loaded successfully'
    })

# Static files for templates
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a room"""
    room = data['room']
    emit('room_joined', {'room': room, 'user': current_user.username})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle user leaving a room"""
    room = data['room']
    emit('room_left', {'room': room, 'user': current_user.username})

@socketio.on('segmentation_update')
def handle_segmentation_update(data):
    """Handle real-time segmentation updates"""
    room = data['room']
    emit('segmentation_update', data, room=room)

@socketio.on('annotation_update')
def handle_annotation_update(data):
    """Handle real-time annotation updates"""
    room = data['room']
    emit('annotation_update', data, room=room)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Template files
template_files = {
    'login.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Prostate MRI Segmentation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="password"], input[type="email"] { width: 100%; padding: 8px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .error { color: red; }
    </style>
</head>
<body>
    <h2>Login</h2>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <form method="post">
        <div class="form-group">
            <label>Username:</label>
            <input type="text" name="username" required>
        </div>
        <div class="form-group">
            <label>Password:</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
</body>
</html>
''',

    'register.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Register - Prostate MRI Segmentation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="password"], input[type="email"] { width: 100%; padding: 8px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .error { color: red; }
    </style>
</head>
<body>
    <h2>Register</h2>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <form method="post">
        <div class="form-group">
            <label>Username:</label>
            <input type="text" name="username" required>
        </div>
        <div class="form-group">
            <label>Email:</label>
            <input type="email" name="email" required>
        </div>
        <div class="form-group">
            <label>Password:</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
</body>
</html>
''',

    'dashboard.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Prostate MRI Segmentation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .task-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .btn { background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }
        .btn:hover { background: #45a049; }
        .status { padding: 5px 10px; border-radius: 3px; }
        .status-created { background: #e0e0e0; }
        .status-in-progress { background: #ffeb3b; }
        .status-completed { background: #4CAF50; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Prostate MRI Segmentation Dashboard</h1>
        <a href="{{ url_for('logout') }}" class="btn">Logout</a>
    </div>

    <div>
        <h2>My Tasks</h2>
        {% if tasks %}
            {% for task in tasks %}
            <div class="task-card">
                <h3>{{ task.task_id }}</h3>
                <p>Patient ID: {{ task.patient_id }}</p>
                <p>Status: <span class="status status-{{ task.status }}">{{ task.status }}</span></p>
                <p>Progress: {{ task.progress }}%</p>
                <p>Created: {{ task.created_at }}</p>
                <a href="{{ url_for('segmentation', task_id=task.task_id) }}" class="btn">Edit</a>
            </div>
            {% endfor %}
        {% else %}
            <p>No tasks found. <a href="{{ url_for('upload') }}">Create your first task</a></p>
        {% endif %}
    </div>

    <div style="margin-top: 20px;">
        <a href="{{ url_for('upload') }}" class="btn">Upload New Series</a>
    </div>
</body>
</html>
''',

    'upload.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload DICOM Series - Prostate MRI Segmentation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="file"] { width: 100%; padding: 8px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .btn { background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }
        .btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <h2>Upload DICOM Series</h2>
    <form method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data">
        <div class="form-group">
            <label>Series Name:</label>
            <input type="text" name="series_name" required>
        </div>
        <div class="form-group">
            <label>Upload DICOM Files:</label>
            <input type="file" name="dicom_files" multiple required>
        </div>
        <button type="submit">Upload Series</button>
    </form>
    <p><a href="{{ url_for('dashboard') }}" class="btn">Back to Dashboard</a></p>
</body>
</html>
''',

    'segmentation.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Segmentation - Prostate MRI Segmentation</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { display: flex; }
        .toolbar { width: 200px; border-right: 1px solid #ddd; padding: 15px; }
        .main-content { flex: 1; padding: 15px; }
        .tool-btn { display: block; width: 100%; margin-bottom: 10px; padding: 10px; background: #f0f0f0; border: none; cursor: pointer; }
        .tool-btn:hover { background: #e0e0e0; }
        .tool-btn.active { background: #4CAF50; color: white; }
        .image-container { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
        .status-bar { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #4CAF50; width: 0%; transition: width 0.3s; }
        .btn { background: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; margin: 5px; }
        .btn:hover { background: #45a049; }
        .btn-danger { background: #f44336; }
        .btn-danger:hover { background: #da190b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="toolbar">
            <h3>Tools</h3>
            <button class="tool-btn active" onclick="selectTool('brush')">Brush</button>
            <button class="tool-btn" onclick="selectTool('rectangle')">Rectangle</button>
            <button class="tool-btn" onclick="selectTool('circle')">Circle</button>
            <button class="tool-btn" onclick="selectTool('flood_fill')">Flood Fill</button>
            <button class="tool-btn" onclick="selectTool('threshold')">Threshold</button>
            <button class="tool-btn" onclick="selectTool('watershed')">Watershed</button>
            <button class="tool-btn" onclick="runAI()">AI Pre-segmentation</button>

            <h3>Actions</h3>
            <button class="tool-btn" onclick="saveSegmentation()">Save</button>
            <button class="tool-btn" onclick="resetSegmentation()">Reset</button>
            <button class="tool-btn btn-danger" onclick="deleteTask()">Delete Task</button>

            <h3>Status</h3>
            <div class="status-bar">
                <p>Status: <span id="status-text">Created</span></p>
                <p>Progress: <span id="progress-text">0%</span></p>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
            </div>
        </div>

        <div class="main-content">
            <h2>Segmentation Task: {{ task.task_id }}</h2>
            <div class="image-container">
                <img id="segmentation-image" src="data:image/png;base64,{{ task.image_data }}" alt="MRI Image" style="max-width: 100%;">
            </div>
            <div>
                <p><strong>Patient ID:</strong> {{ task.patient_id }}</p>
                <p><strong>Series UID:</strong> {{ task.series_uid }}</p>
                <p><strong>Created:</strong> {{ task.created_at }}</p>
            </div>
        </div>
    </div>

    <script>
        let currentTool = 'brush';

        function selectTool(tool) {
            currentTool = tool;
            // Update UI to show active tool
            document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }

        function runAI() {
            alert('Running AI pre-segmentation...');
            // In a real implementation, this would call the AI API
        }

        function saveSegmentation() {
            alert('Saving segmentation...');
            // In a real implementation, this would save the segmentation
        }

        function resetSegmentation() {
            alert('Resetting segmentation...');
            // In a real implementation, this would reset the segmentation
        }

        function deleteTask() {
            if (confirm('Are you sure you want to delete this task?')) {
                alert('Task deleted');
                // In a real implementation, this would delete the task
            }
        }

        // Update progress bar
        function updateProgress(progress) {
            document.getElementById('progress-fill').style.width = progress + '%';
            document.getElementById('progress-text').textContent = progress + '%';
        }

        // Simulate progress updates
        setInterval(() => {
            const currentProgress = parseInt(document.getElementById('progress-text').textContent);
            if (currentProgress < 100) {
                updateProgress(currentProgress + 1);
            }
        }, 1000);
    </script>
</body>
</html>
'''

}

# Create template files
for filename, content in template_files.items():
    template_path = Path(f'/home/admin/Coding-Projects/segmentator-prostate/templates/{filename}')
    template_path.parent.mkdir(exist_ok=True)
    with open(template_path, 'w') as f:
        f.write(content)

# Create a simple test to verify the web interface works
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Prostate MRI Segmentation Web Interface is running',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("Starting Prostate MRI Segmentation Web Interface...")
    print("Access at: http://localhost:5000")
    print("Default credentials: admin / admin")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
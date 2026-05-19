"""
Web interface for multi-user prostate MRI segmentation tool
Provides REST API and real-time collaboration features
"""

from flask import Flask, request, jsonify, session, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import json
from datetime import datetime
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///segmentation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for database storage
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin, researcher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Task model for segmentation tasks
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
    annotations = db.Column(db.Text)  # JSON string
    segments = db.Column(db.Text)  # JSON string

    def __repr__(self):
        return f'<SegmentationTask {self.task_id}>'

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
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prostate MRI Segmentation Tool</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body>
        <h1>Prostate MRI Segmentation Tool</h1>
        <div id="status">Connected</div>
        <div id="messages"></div>
        <script>
            const socket = io();

            socket.on('connect', function() {
                $('#status').text('Connected to server');
            });

            socket.on('message', function(data) {
                $('#messages').append('<p>' + data.msg + '</p>');
            });

            socket.on('task_update', function(data) {
                $('#messages').append('<p>Task updated: ' + data.task_id + '</p>');
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login endpoint"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.is_active:
            # In a real implementation, you would verify the password
            # For now, we'll assume it's valid
            login_user(user)
            return jsonify({'success': True, 'message': 'Logged in successfully'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})

    return render_template_string('''
    <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    ''')

@app.route('/logout')
@login_required
def logout():
    """User logout endpoint"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# API endpoints for segmentation tasks
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get all segmentation tasks"""
    tasks = SegmentationTask.query.all()
    return jsonify([{
        'id': task.id,
        'task_id': task.task_id,
        'patient_id': task.patient_id,
        'series_uid': task.series_uid,
        'created_by': task.created_by,
        'created_at': task.created_at.isoformat(),
        'status': task.status,
        'progress': task.progress
    } for task in tasks])

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
    task = SegmentationTask.query.filter_by(task_id=task_id).first()
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

    task.last_updated = datetime.utcnow()
    db.session.commit()

    # Emit real-time update
    socketio.emit('task_update', {
        'task_id': task.task_id,
        'status': task.status,
        'progress': task.progress
    })

    return jsonify({'success': True, 'message': 'Task updated successfully'})

@app.route('/api/tasks/<task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get a specific segmentation task"""
    task = SegmentationTask.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404

    return jsonify({
        'task_id': task.task_id,
        'patient_id': task.patient_id,
        'series_uid': task.series_uid,
        'created_by': task.created_by,
        'created_at': task.created_at.isoformat(),
        'status': task.status,
        'progress': task.progress,
        'annotations': json.loads(task.annotations) if task.annotations else [],
        'segments': json.loads(task.segments) if task.segments else []
    })

# SocketIO events for real-time collaboration
@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a room"""
    room = data['room']
    join_room(room)
    emit('room_joined', {'room': room, 'user': current_user.username})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle user leaving a room"""
    room = data['room']
    leave_room(room)
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

# Web-based AI pre-segmentation endpoint
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
    time.sleep(2)

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

# Web-based DICOM handling endpoint
@app.route('/api/dicom/load', methods=['POST'])
@login_required
def load_dicom_series():
    """Load DICOM series for segmentation"""
    # This would handle loading DICOM data from uploaded files or directories
    return jsonify({
        'success': True,
        'message': 'DICOM series loaded successfully'
    })

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
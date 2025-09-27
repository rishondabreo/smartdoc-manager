from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import json

from config import Config
from models.user import User, users_db
from utils.file_validator import FileValidator

app = Flask(__name__)
app.config.from_object(Config)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize services
file_validator = FileValidator()

def get_storage_client():
    """Get storage client with comprehensive error handling"""
    try:
        return storage.Client()
    except DefaultCredentialsError:
        return None
    except Exception as e:
        print(f"Storage client error: {e}")
        return None

def get_bucket():
    """Get Cloud Storage bucket with error handling"""
    try:
        client = get_storage_client()
        if not client:
            return None
            
        bucket_name = app.config['BUCKET_NAME']
        bucket = client.bucket(bucket_name)
        
        if not bucket.exists():
            try:
                bucket = client.create_bucket(bucket_name)
                print(f"Created new bucket: {bucket_name}")
            except Exception as e:
                print(f"Error creating bucket: {e}")
                return None
                
        return bucket
    except Exception as e:
        print(f"Bucket error: {e}")
        return None

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            user = users_db['1']
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        bucket = get_bucket()
        if not bucket:
            flash('Could not connect to Google Cloud Storage.', 'error')
            return render_template('dashboard.html', documents=[], total_docs=0, total_size=0)
        
        blobs = list(bucket.list_blobs())
        documents = []
        total_size = 0
        
        for blob in blobs:
            metadata = blob.metadata or {}
            doc_type = blob.name.split('.')[-1] if '.' in blob.name else 'unknown'
            
            document = {
                'id': blob.name,
                'name': blob.name.split('_', 1)[1] if '_' in blob.name else blob.name,
                'storage_name': blob.name,
                'size': blob.size,
                'type': doc_type,
                'upload_date': blob.time_created,
                'url': blob.public_url
            }
            
            documents.append(document)
            total_size += blob.size
        
        total_size_mb = round(total_size / (1024 * 1024), 2)
        return render_template('dashboard.html', 
                             documents=documents, 
                             total_docs=len(documents),
                             total_size=total_size_mb,
                             user=current_user)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', documents=[], total_docs=0, total_size=0)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    bucket = get_bucket()
    if not bucket:
        return jsonify({'error': 'Storage not available.'}), 500
    
    try:
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        blob = bucket.blob(unique_filename)
        blob.upload_from_string(file.read(), content_type=file.content_type)
        blob.make_public()
        
        flash(f'File {original_filename} uploaded successfully!', 'success')
        return jsonify({
            'success': True,
            'filename': original_filename,
            'url': blob.public_url
        })
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# FIXED DOWNLOAD ROUTE
@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    """Download a file"""
    try:
        bucket = get_bucket()
        if not bucket:
            flash('Storage not available', 'error')
            return redirect(url_for('dashboard'))
        
        blob = bucket.blob(filename)
        if blob.exists():
            # Use public URL for direct download
            if not blob.public_url:
                blob.make_public()
            return redirect(blob.public_url)
        else:
            flash('File not found', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# FIXED DELETE ROUTE
@app.route('/delete/<path:filename>')
@login_required
def delete_file(filename):
    """Delete a file"""
    try:
        bucket = get_bucket()
        if not bucket:
            flash('Storage not available', 'error')
            return redirect(url_for('dashboard'))
        
        blob = bucket.blob(filename)
        if blob.exists():
            original_name = filename.split('_', 1)[1] if '_' in filename else filename
            blob.delete()
            flash(f'File {original_name} deleted successfully!', 'success')
        else:
            flash('File not found', 'error')
    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
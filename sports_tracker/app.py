import os
import sys
from flask import Flask, render_template, Response, request, jsonify, send_from_directory

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Initialize Flask app with correct static file configuration
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Configuration
app.config.update({
    'UPLOAD_FOLDER': os.path.join('static', 'uploads'),
    'MAX_CONTENT_LENGTH': 500 * 1024 * 1024,
    'ALLOWED_EXTENSIONS': {'mp4', 'mov', 'avi'},
    'JSONIFY_PRETTYPRINT_REGULAR': True
})

# Import SportsTracker after setting up paths
try:
    from tracker.core import SportsTracker
except ImportError:
    sys.path.insert(0, os.path.abspath('.'))
    from tracker.core import SportsTracker

# Initialize tracker
tracker = SportsTracker()


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with correct routing"""
    return send_from_directory(app.static_folder, filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith(tuple(app.config['ALLOWED_EXTENSIONS'])):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        success, message = tracker.process_video(filename, filename + '_processed.mp4')

        if success:
            return jsonify({
                'success': True,
                'message': message,
                'output_path': '/video_feed/' + os.path.basename(filename) + '_processed.mp4'
            })
        return jsonify({'error': message}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/video_feed/<filename>')
def video_feed(filename):
    """Stream processed video"""
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return Response(tracker.generate_frames(video_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Print debug information
    print(f"Static folder: {os.path.abspath(app.static_folder)}")
    print(f"Template folder: {os.path.abspath(app.template_folder)}")

    app.run(host='0.0.0.0', port=5000, debug=True)
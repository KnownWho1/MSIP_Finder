from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tempfile
from pathlib import Path
import shutil

from utils.scanner import LabelScanner

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

scanner = LabelScanner()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    temp_dir = None
    try:
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return render_template('results.html', results=[], error='No files selected')
        
        # Create a temporary directory that will be deleted after processing
        temp_dir = Path(tempfile.mkdtemp(prefix='msip_upload_'))
        results = scanner.scan_files_flask(files, base_temp_dir=temp_dir)
        return render_template('results.html', results=results)
    except Exception as e:
        return render_template('results.html', results=[], error=str(e))
    finally:
        # Ensure no uploaded data is retained
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

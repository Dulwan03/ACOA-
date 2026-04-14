from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import sys
import os
import threading
import queue
import json
import re
from datetime import datetime
import io
import csv
import zipfile
import glob
from contextlib import redirect_stdout

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.parallelism_module import run_parallelism_experiment
from modules.scheduling_module import run_scheduling_experiment
from modules.bus_module import run_bus_experiment
from modules.cache_module import run_cache_experiment
from modules.performance_module import plot_parallelism_results, print_results
from utils import ensure_directories

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Ensure output directories exist
ensure_directories()

# Global variables for progress tracking
execution_queue = queue.Queue()
current_execution = {
    'status': 'idle',
    'module': None,
    'progress': 0,
    'results': None,
    'error': None,
    'start_time': None,
    'is_batch': False,
    'batch_results': {},  # Store results for all modules when running all
    'modules_completed': 0,
    'total_modules': 0
}


class ExecutionThread(threading.Thread):
    """Thread for running experiments without blocking the Flask app"""
    def __init__(self, module_name, parameters=None):
        super().__init__(daemon=True)
        self.module_name = module_name
        self.parameters = parameters or {}
        self.results = None
        self.error = None

    def run(self):
        try:
            current_execution['status'] = 'running'
            current_execution['module'] = self.module_name
            current_execution['progress'] = 10
            current_execution['start_time'] = datetime.now().isoformat()

            # Capture stdout from experiments
            output_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer):
                    if self.module_name == 'parallelism':
                        run_parallelism_experiment()
                    elif self.module_name == 'scheduling':
                        run_scheduling_experiment()
                    elif self.module_name == 'bus':
                        run_bus_experiment()
                    elif self.module_name == 'cache':
                        run_cache_experiment()
            except Exception as e:
                output_buffer.write(f"\nError during execution: {str(e)}")
            
            # Store captured output as results
            self.results = output_buffer.getvalue()
            
            current_execution['progress'] = 100
            
            # If running batch, add to batch results; otherwise replace
            if current_execution.get('is_batch'):
                current_execution['batch_results'][self.module_name] = self.results
                current_execution['modules_completed'] = len(current_execution['batch_results'])
                # Create aggregated display
                current_execution['results'] = self._create_batch_report()
            else:
                current_execution['results'] = self.results
                
            current_execution['status'] = 'completed'

        except Exception as e:
            self.error = str(e)
            current_execution['status'] = 'error'
            current_execution['error'] = str(e)

    def _create_batch_report(self):
        """Create a formatted report of all batch results"""
        report = "╔" + "═" * 78 + "╗\n"
        report += "║" + " BATCH EXECUTION REPORT ".center(78) + "║\n"
        report += "╚" + "═" * 78 + "╝\n\n"
        
        for idx, (module_name, results) in enumerate(current_execution['batch_results'].items(), 1):
            report += f"\n{'─' * 80}\n"
            report += f"[{idx}] {module_name.upper()} MODULE\n"
            report += f"{'─' * 80}\n"
            report += results + "\n"
        
        report += f"\n{'═' * 80}\n"
        report += f"Total Modules Completed: {len(current_execution['batch_results'])}\n"
        report += f"{'═' * 80}\n"
        
        return report


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/upload-images', methods=['POST'])
def upload_images():
    """API endpoint to upload images"""
    try:
        # Check if files are in the request
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        
        if not files:
            return jsonify({'error': 'No images provided'}), 400
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Outputs', 'Images')
        os.makedirs(output_dir, exist_ok=True)
        
        uploaded_count = 0
        max_size = 10 * 1024 * 1024  # 10MB
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
        
        for file in files:
            # Validate file
            if not file or file.filename == '':
                continue
            
            # Get file extension
            if '.' not in file.filename:
                continue
            
            ext = file.filename.rsplit('.', 1)[1].lower()
            
            if ext not in allowed_extensions:
                continue
            
            # Check file size (10MB limit)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > max_size:
                continue
            
            # Save file
            try:
                # Create sanitized filename
                filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
                filepath = os.path.join(output_dir, filename)
                file.save(filepath)
                uploaded_count += 1
            except Exception as e:
                continue
        
        return jsonify({
            'success': True,
            'uploaded': uploaded_count,
            'message': f'Successfully uploaded {uploaded_count} image(s) to Outputs/Images folder'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-experiment', methods=['POST'])
def run_experiment():
    """API endpoint to run an experiment"""
    data = request.json
    module_name = data.get('module')
    parameters = data.get('parameters', {})

    if not module_name or module_name not in ['parallelism', 'scheduling', 'bus', 'cache']:
        return jsonify({'error': 'Invalid module name'}), 400

    # Check if already running
    if current_execution['status'] == 'running':
        return jsonify({'error': 'An experiment is already running'}), 400

    # Allow starting if previous experiment is completed, error, or idle
    if current_execution['status'] not in ['completed', 'error', 'idle', 'stopped']:
        return jsonify({'error': f'Invalid state: {current_execution["status"]}'}), 400

    # Start execution in background thread
    exec_thread = ExecutionThread(module_name, parameters)
    exec_thread.start()

    return jsonify({
        'success': True,
        'message': f'Started {module_name} experiment',
        'module': module_name
    })


@app.route('/api/run-batch', methods=['POST'])
def run_batch():
    """API endpoint to run all modules sequentially"""
    data = request.json
    parameters = data.get('parameters', {})

    # Check if already running
    if current_execution['status'] == 'running':
        return jsonify({'error': 'An experiment is already running'}), 400

    # Allow starting if previous experiment is completed, error, or idle
    if current_execution['status'] not in ['completed', 'error', 'idle', 'stopped']:
        return jsonify({'error': f'Invalid state: {current_execution["status"]}'}), 400

    # Reset for batch execution
    current_execution['is_batch'] = True
    current_execution['batch_results'] = {}
    current_execution['modules_completed'] = 0
    current_execution['total_modules'] = 4
    current_execution['start_time'] = datetime.now().isoformat()

    return jsonify({
        'success': True,
        'message': 'Batch execution initialized',
        'modules': ['parallelism', 'scheduling', 'bus', 'cache']
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current execution status"""
    return jsonify({
        'status': current_execution['status'],
        'module': current_execution['module'],
        'progress': current_execution['progress'],
        'results': current_execution['results'],
        'error': current_execution['error'],
        'start_time': current_execution['start_time']
    })


@app.route('/api/stop', methods=['POST'])
def stop_execution():
    """Stop current execution (if possible)"""
    current_execution['status'] = 'stopped'
    return jsonify({'success': True, 'message': 'Stop requested'})


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset execution state"""
    current_execution['status'] = 'idle'
    current_execution['module'] = None
    current_execution['progress'] = 0
    current_execution['results'] = None
    current_execution['error'] = None
    current_execution['start_time'] = None
    current_execution['is_batch'] = False
    current_execution['batch_results'] = {}
    current_execution['modules_completed'] = 0
    current_execution['total_modules'] = 0
    return jsonify({'success': True, 'message': 'Reset complete'})


@app.route('/api/download-results', methods=['GET'])
def download_results():
    """Download results as CSV"""
    if current_execution['results'] is None:
        return jsonify({'error': 'No results available'}), 400

    try:
        # Convert results to CSV format
        output = io.StringIO()
        writer = csv.writer(output)

        results = current_execution['results']
        
        # If results is a string (from captured output), write it as-is with some formatting
        if isinstance(results, str):
            writer.writerow(['Experiment Output'])
            for line in results.split('\n'):
                if line.strip():
                    writer.writerow([line])
        elif isinstance(results, dict):
            for key, value in results.items():
                writer.writerow([key, value])
        elif isinstance(results, list):
            for item in results:
                writer.writerow([str(item)])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"results_{current_execution['module']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/graphs', methods=['GET'])
def get_graphs():
    """Get available graphs"""
    graphs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Outputs', 'Graphs')
    
    if not os.path.exists(graphs_dir):
        return jsonify({})
    
    graphs = {}
    for graph_file in glob.glob(os.path.join(graphs_dir, '*.png')):
        graph_name = os.path.splitext(os.path.basename(graph_file))[0]
        # Return relative URL path
        graphs[graph_name.replace('_', ' ').title()] = f'/graphs/{os.path.basename(graph_file)}'
    
    return jsonify(graphs)


@app.route('/graphs/<filename>')
def get_graph_image(filename):
    """Serve graph images"""
    graphs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Outputs', 'Graphs')
    filepath = os.path.join(graphs_dir, filename)
    
    # Security: ensure the file is within the graphs directory
    if not os.path.abspath(filepath).startswith(os.path.abspath(graphs_dir)):
        return jsonify({'error': 'Forbidden'}), 403
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Graph not found'}), 404
    
    return send_file(filepath, mimetype='image/png')


@app.route('/api/download-graphs', methods=['GET'])
def download_graphs():
    """Download all graphs as zip"""
    graphs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Outputs', 'Graphs')
    
    if not os.path.exists(graphs_dir) or not glob.glob(os.path.join(graphs_dir, '*.png')):
        return jsonify({'error': 'No graphs available'}), 404
    
    try:
        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for graph_file in glob.glob(os.path.join(graphs_dir, '*.png')):
                arcname = os.path.basename(graph_file)
                zip_file.write(graph_file, arcname=arcname)
        
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"graphs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create-report', methods=['POST'])
def create_report():
    """Create a summary report of results"""
    if current_execution['results'] is None:
        return jsonify({'error': 'No results available'}), 400

    report = {
        'timestamp': datetime.now().isoformat(),
        'module': current_execution['module'],
        'status': current_execution['status'],
        'start_time': current_execution['start_time'],
        'results': current_execution['results'],
        'summary': f"{current_execution['module'].capitalize()} experiment completed successfully"
    }

    return jsonify(report)


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

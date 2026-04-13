# Web UI for Parallel Computing Demonstration

A modern Flask-based web interface for the Parallel Computing Demonstration Application.

## Features

✨ **Interactive Web Interface**
- Clean, modern UI with real-time updates
- Run experiments individually or all at once
- Visual progress tracking
- Live execution logs

⚙️ **Experiment Control**
- Parallelism experiments
- Scheduling experiments
- Bus system experiments
- Cache experiments
- Configurable parameters (workers, iterations)

📊 **Results Management**
- Real-time results display
- Download results as CSV
- Generate execution reports
- Save reports as text files

## Directory Structure

```
Final project ACOA/
├── app/
│   ├── app.py                 # Flask application
│   ├── templates/
│   │   └── index.html         # Main HTML template
│   └── static/
│       ├── styles.css         # CSS styling
│       └── script.js          # JavaScript logic
├── modules/                   # Original experiment modules
│   ├── parallelism_module.py
│   ├── scheduling_module.py
│   ├── bus_module.py
│   ├── cache_module.py
│   └── performance_module.py
├── main.py                    # Original CLI application
├── utils.py                   # Utility functions
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Steps

1. **Navigate to the project directory:**
   ```bash
   cd "d:\SLIIT CSE\Advance computer organization and architechure\Final project ACOA"
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   **Windows (PowerShell):**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
   
   **Windows (Command Prompt):**
   ```bash
   .\venv\Scripts\activate.bat
   ```
   
   **Mac/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server:**
   ```bash
   python app/app.py
   ```

   You should see output similar to:
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: on
   ```

2. **Open your web browser and navigate to:**
   ```
   http://127.0.0.1:5000
   ```

3. **Use the interface to:**
   - Click any experiment button to run individual module
   - Click "Run All Modules" to execute all experiments sequentially
   - Adjust parameters before running (workers, iterations)
   - Monitor progress in real-time
   - View results and download as CSV
   - Generate and download reports

## API Endpoints

### Experiment Control
- **POST** `/api/run-experiment` - Start an experiment
  - Body: `{"module": "parallelism|scheduling|bus|cache", "parameters": {...}}`
  
- **POST** `/api/stop` - Stop current execution

- **POST** `/api/reset` - Reset execution state

### Status & Results
- **GET** `/api/status` - Get current execution status

- **GET** `/api/download-results` - Download results as CSV

- **POST** `/api/create-report` - Generate execution report

## Usage Tips

1. **Parameters**: Adjust workers and iterations before running for custom configurations

2. **Sequential Execution**: "Run All Modules" runs experiments one after another (not in parallel)

3. **Results**: Results are displayed immediately upon completion and remain available

4. **Downloads**: Use "Download Results" to export CSV data for analysis

5. **Reports**: Generate reports to capture complete execution details with timestamp

## Troubleshooting

### Port Already in Use
If port 5000 is in use, modify the Flask app launch:
```python
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)  # Change port number
```

### Module Import Errors
Ensure you're running the Flask app from the correct directory and the virtual environment is activated.

### Slow Performance
- Reduce the number of iterations
- Close other applications to free up resources
- Check system memory usage with Task Manager

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Any modern Chromium-based browser

## Project Structure Notes

- **Flask Backend**: Handles experiment execution in background threads
- **REST API**: Provides endpoints for UI communication
- **Server-Sent Events**: Real-time progress updates (can be enhanced)
- **Static Frontend**: Pure HTML/CSS/JavaScript (no build step required)

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Graph visualization in web UI
- [ ] Database support for result history
- [ ] User authentication
- [ ] Comparison between different runs
- [ ] Configuration presets
- [ ] Batch experiment scheduling

## Notes

- The application runs experiments in background threads to avoid blocking the UI
- Results are stored in memory during execution
- Large result sets may be truncated in the UI (use CSV download for full data)

## Support

For issues or questions:
1. Check the execution logs in the UI
2. Review the browser console (F12) for JavaScript errors
3. Check Flask server output in terminal for backend errors

---

**Course**: Advanced Computer Organization & Architecture  
**Institution**: SLIIT CSE  
**Project**: Final Project ACOA

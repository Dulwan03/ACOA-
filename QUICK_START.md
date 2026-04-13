# Quick Start Guide - Web UI for Parallel Computing

## ⚡ Fastest Way to Get Started

### Windows Users
1. Navigate to the project folder in File Explorer
2. Double-click **`run_web_ui.bat`**
3. Wait for the message: "Open your browser and go to http://127.0.0.1:5000"
4. Open your browser and visit: **http://127.0.0.1:5000**

### Mac/Linux Users
1. Open Terminal in the project folder
2. Run: `bash run_web_ui.sh`
3. Wait for the message showing the URL
4. Open your browser and visit: **http://127.0.0.1:5000**

---

## Manual Setup (If Above Doesn't Work)

### Windows PowerShell
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the app
python app/app.py
```

### Windows Command Prompt
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
python app/app.py
```

### Mac/Linux Terminal
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/app.py
```

---

## What Each Program Does

| Module | Description |
|--------|-------------|
| **Parallelism** | Tests parallel processing with multiple workers |
| **Scheduling** | Tests task scheduling and execution timing |
| **Bus** | Simulates bus system performance |
| **Cache** | Tests cache efficiency and hit rates |

---

## UI Features

### 🎯 Run Experiments
- Click any button to run that module
- Click "Run All Modules" to run all experiments sequentially

### ⚙️ Configure Parameters
- **Workers**: Number of parallel workers (1-16)
- **Iterations**: Number of iterations to run (1-1000)

### 📊 Monitor Progress
- Real-time progress bar
- Current module information
- Execution time tracking
- Live execution logs

### 💾 Download Results
- **Download Results** → CSV file with raw data
- **Generate Report** → Text report with full details

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Port 5000 already in use" | Close other Flask apps or modify port in `app/app.py` |
| "Module not found" | Make sure virtual environment is activated |
| "Can't connect to localhost:5000" | Check Flask server is running in terminal |
| "Permission denied" on `.sh` file | Run `chmod +x run_web_ui.sh` first |

---

## Browser Tips

- Use **Chrome, Firefox, or Edge** for best experience
- Press **F12** to see Logs if something's not working
- Results update in **real-time** as experiments run
- Download buttons become active after experiments complete

---

**That's it! You're ready to go!** 🚀

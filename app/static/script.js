// ============================================
// Parallel Computing UI - JavaScript
// ============================================

const API_BASE = 'http://127.0.0.1:5000/api';
let statusCheckInterval = null;
let elapsedTimeInterval = null;
let startTimeGlobal = null;

// ============= INITIALIZATION =============
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    log('Application initialized successfully', 'info');
});

function initializeEventListeners() {
    // Experiment buttons
    document.querySelectorAll('.experiment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const module = this.dataset.module;
            runExperiment(module);
        });
    });

    // Action buttons
    document.getElementById('runAllBtn').addEventListener('click', runAllModules);
    document.getElementById('stopBtn').addEventListener('click', stopExecution);
    document.getElementById('resetBtn').addEventListener('click', resetExecution);

    // Download and Report buttons
    document.getElementById('downloadBtn').addEventListener('click', downloadResults);
    document.getElementById('reportBtn').addEventListener('click', generateReport);

    // Graphs buttons
    document.getElementById('refreshGraphsBtn').addEventListener('click', refreshGraphs);
    document.getElementById('downloadGraphsBtn').addEventListener('click', downloadGraphs);

    // Upload area buttons
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    document.getElementById('uploadBtn').addEventListener('click', uploadImages);
    document.getElementById('clearUploadBtn').addEventListener('click', clearUploadArea);

    // Drag and drop
    uploadArea.addEventListener('click', () => imageInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    imageInput.addEventListener('change', handleFileSelect);

    // Modal
    document.querySelector('.close-btn').addEventListener('click', closeModal);
    document.getElementById('closeReportBtn').addEventListener('click', closeModal);
    document.getElementById('downloadReportBtn').addEventListener('click', downloadReportAsFile);

    // Click outside modal to close
    document.getElementById('reportModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });

    // Initialize collapsible output images
    initializeCollapsibleOutputImages();
}

// ============= MAIN FUNCTIONS =============
async function runExperiment(moduleName) {
    if (!moduleName) {
        log('Invalid module name', 'error');
        return;
    }

    const params = {
    };

    try {
        disableAllControls();
        showProcessingStatus(moduleName);
        log(`Starting ${moduleName} experiment...`, 'info');

        const response = await fetch(`${API_BASE}/run-experiment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                module: moduleName,
                parameters: params
            })
        });

        if (!response.ok) {
            throw new Error('Failed to start experiment');
        }

        const data = await response.json();
        const imageSource = data.image_used === 'uploaded' ? 'uploaded image' : 'default image (data/input.jpg)';
        log(`${moduleName} experiment started using ${imageSource}`, 'success');
        startStatusMonitoring();

    } catch (error) {
        log(`Error starting experiment: ${error.message}`, 'error');
        hideProcessingStatus();
        enableAllControls();
    }
}

async function runAllModules() {
    const modules = ['parallelism', 'scheduling', 'bus', 'cache'];
    const params = {
    };

    disableAllControls();
    showProcessingStatus('All Modules');
    log('🚀 Starting batch execution of all modules...', 'info');

    try {
        // Initialize batch mode
        const batchResponse = await fetch(`${API_BASE}/run-batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ parameters: params })
        });

        if (!batchResponse.ok) {
            const error = await batchResponse.json();
            throw new Error(error.error || 'Failed to initialize batch');
        }

        log(`📋 Batch initialized - Running ${modules.length} modules`, 'info');

        // Run each module sequentially
        for (let i = 0; i < modules.length; i++) {
            const module = modules[i];
            try {
                log(`[${i + 1}/${modules.length}] ▶ Starting ${module.toUpperCase()} experiment...`, 'info');
                
                const response = await fetch(`${API_BASE}/run-experiment`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        module: module,
                        parameters: params
                    })
                });

                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `Failed to start ${module}`);
                }

                const imageSource = module === 'parallelism' 
                    ? (data.image_used === 'uploaded' ? ' (uploaded image)' : ' (default image)')
                    : '';
                log(`${module} experiment started${imageSource}`, 'info');
                
                // Start monitoring for this module
                startStatusMonitoring();
                
                // Wait for this module to complete
                await waitForCompletion();
                
                log(`[${i + 1}/${modules.length}] ✓ ${module.toUpperCase()} completed`, 'success');
                
                // Stop monitoring before next module
                stopStatusMonitoring();
                
                // Refresh output images after each module completes (especially for parallelism)
                if (module === 'parallelism') {
                    await loadOutputImages();
                }
                
                // Add a small delay between modules
                if (i < modules.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
                
            } catch (error) {
                log(`[${i + 1}/${modules.length}] ✗ Error with ${module}: ${error.message}`, 'error');
                stopStatusMonitoring();
                break;
            }
        }

        log('✓ All modules execution completed! View the aggregated report.', 'success');
        
        // Enable download and report buttons
        resetDownloadButtons(true);
        
    } catch (error) {
        log(`⚠️ Batch initialization failed: ${error.message}`, 'error');
    }

    enableAllControls();
}

async function stopExecution() {
    try {
        const response = await fetch(`${API_BASE}/stop`, {
            method: 'POST'
        });

        if (response.ok) {
            log('Execution stopped by user', 'warning');
            stopStatusMonitoring();
            hideProcessingStatus();
            enableAllControls();
        }
    } catch (error) {
        log(`Error stopping execution: ${error.message}`, 'error');
    }
}

async function resetExecution() {
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST'
        });

        if (response.ok) {
            stopStatusMonitoring();
            hideProcessingStatus();
            clearResults();
            updateStatus('idle', 'Ready');
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = '0%';
            document.getElementById('currentModule').textContent = 'None';
            document.getElementById('currentStatus').textContent = 'Idle';
            document.getElementById('startTime').textContent = '-';
            document.getElementById('elapsedTime').textContent = '-';
            enableAllControls();
            log('Application reset', 'info');
        }
    } catch (error) {
        log(`Error resetting: ${error.message}`, 'error');
    }
}

// ============= STATUS MONITORING =============
function startStatusMonitoring() {
    clearInterval(statusCheckInterval);
    clearInterval(elapsedTimeInterval);

    // Check status every 500ms
    statusCheckInterval = setInterval(updateExecutionStatus, 500);

    // Update elapsed time every second
    elapsedTimeInterval = setInterval(updateElapsedTime, 1000);
}

function stopStatusMonitoring() {
    clearInterval(statusCheckInterval);
    clearInterval(elapsedTimeInterval);
}

async function updateExecutionStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const status = await response.json();

        // Update UI with status
        updateStatus(status.status, status.module);

        // Update progress bar
        const progress = status.progress || 0;
        document.getElementById('progressFill').style.width = progress + '%';
        document.getElementById('progressText').textContent = progress + '%';

        // Update module info
        document.getElementById('currentModule').textContent = status.module || 'None';
        document.getElementById('currentStatus').textContent = capitalizeFirst(status.status);

        // Update start time
        if (status.start_time && !startTimeGlobal) {
            startTimeGlobal = new Date(status.start_time);
            document.getElementById('startTime').textContent = startTimeGlobal.toLocaleTimeString();
        }

        // Update results if available
        if (status.results) {
            displayResults(status.results);
            resetDownloadButtons(true);
        }

        // Handle completion
        if (status.status === 'completed' || status.status === 'error') {
            stopStatusMonitoring();
            hideProcessingStatus();
            enableAllControls();
            
            // Load output images after completion
            if (status.status === 'completed') {
                loadOutputImages();
                
                // Auto-refresh graphs for parallelism module
                if (status.module === 'parallelism') {
                    await refreshGraphs();
                }
                
                log(`${status.module} experiment completed successfully`, 'success');
            } else {
                log(`${status.module} experiment failed: ${status.error}`, 'error');
            }
        }

    } catch (error) {
        log(`Error fetching status: ${error.message}`, 'error');
    }
}

function updateElapsedTime() {
    if (startTimeGlobal) {
        const now = new Date();
        const elapsed = Math.floor((now - startTimeGlobal) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('elapsedTime').textContent = 
            `${minutes}m ${seconds}s`;
    }
}

// ============= UI UPDATES =============
function updateStatus(status, module) {
    const badge = document.getElementById('statusBadge');
    const dot = badge.querySelector('.status-dot');
    const text = badge.querySelector('.status-text');

    // Remove all status classes
    dot.classList.remove('idle', 'running', 'completed', 'error');

    switch(status) {
        case 'running':
            dot.classList.add('running');
            text.textContent = `Running: ${module}`;
            break;
        case 'completed':
            dot.classList.add('completed');
            text.textContent = 'Completed';
            break;
        case 'error':
            dot.classList.add('error');
            text.textContent = 'Error';
            break;
        default:
            dot.classList.add('idle');
            text.textContent = 'Ready';
    }
}

function displayResults(results) {
    const resultsDisplay = document.getElementById('resultsDisplay');
    const resultsTabs = document.getElementById('resultsTabs');
    resultsDisplay.innerHTML = '';
    resultsTabs.innerHTML = '';

    let isBatchResults = false;
    let moduleNames = [];

    // Check if results contain multiple modules (batch mode)
    if (typeof results === 'string' && (results.includes('BATCH EXECUTION REPORT') || results.includes('MODULE'))) {
        isBatchResults = true;
        
        // Extract module names from the batch report
        const moduleEntries = [];
        const lines = results.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line.includes('MODULE')) {
                const match = line.match(/\[\d+\]\s*(\w+)\s*MODULE/i);
                if (match) {
                    const moduleName = match[1].toLowerCase();
                    if (!moduleNames.includes(moduleName)) {
                        moduleNames.push(moduleName);
                    }
                    
                    // Extract content until next module or end section marker
                    let content = '';
                    for (let j = i + 1; j < lines.length; j++) {
                        if (lines[j].includes('MODULE') || lines[j].includes('Total Modules') || lines[j].includes('═')) {
                            break;
                        }
                        if (!lines[j].includes('─')) {
                            content += lines[j] + '\n';
                        }
                    }
                    
                    moduleEntries.push({
                        name: moduleName,
                        content: content.trim(),
                        displayName: moduleName.charAt(0).toUpperCase() + moduleName.slice(1)
                    });
                }
            }
        }

        // Store module sections for tab switching
        const moduleSections = {};
        moduleEntries.forEach(entry => {
            moduleSections[entry.name] = entry.content;
        });

        // Create tabs for each module found
        if (moduleNames.length > 0) {
            moduleNames.forEach((moduleName, index) => {
                const entry = moduleEntries.find(e => e.name === moduleName);
                const tab = document.createElement('button');
                tab.className = `result-tab ${index === 0 ? 'active' : ''}`;
                tab.textContent = entry ? entry.displayName : moduleName;
                tab.onclick = () => selectResultTab(moduleName, moduleSections);
                resultsTabs.appendChild(tab);
            });

            // Display first module by default
            selectResultTab(moduleNames[0], moduleSections);
        } else {
            // Fallback to regular display if no modules found
            const pre = document.createElement('pre');
            pre.style.cssText = `
                background: #f1f5f9;
                padding: 1rem;
                border-radius: 6px;
                border-left: 4px solid #2563eb;
                overflow: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.85rem;
                line-height: 1.4;
            `;
            pre.textContent = results;
            resultsDisplay.appendChild(pre);
        }
    } else if (typeof results === 'string') {
        // Single module result
        const pre = document.createElement('pre');
        pre.style.cssText = `
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 6px;
            border-left: 4px solid #2563eb;
            overflow: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            line-height: 1.4;
        `;
        pre.textContent = results;
        resultsDisplay.appendChild(pre);
    } else if (typeof results === 'object' && results !== null) {
        const items = Array.isArray(results) ? results : Object.entries(results);
        
        items.forEach(item => {
            if (Array.isArray(item)) {
                const [key, value] = item;
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `
                    <span class="key">${escapeHtml(key)}:</span>
                    <span class="value">${escapeHtml(formatValue(value))}</span>
                `;
                resultsDisplay.appendChild(div);
            } else {
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `<span class="value">${escapeHtml(item)}</span>`;
                resultsDisplay.appendChild(div);
            }
        });
    } else {
        resultsDisplay.innerHTML = `<pre>${escapeHtml(String(results))}</pre>`;
    }
}

function selectResultTab(moduleName, moduleSections) {
    // Update active tab
    document.querySelectorAll('.result-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.textContent.toLowerCase() === moduleName.toLowerCase()) {
            tab.classList.add('active');
        }
    });

    // Display module results
    const resultsDisplay = document.getElementById('resultsDisplay');
    resultsDisplay.innerHTML = '';

    const content = moduleSections[moduleName] || 'No results available for this module';
    const pre = document.createElement('pre');
    pre.style.cssText = `
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #2563eb;
        overflow: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        line-height: 1.4;
    `;
    pre.textContent = content;
    resultsDisplay.appendChild(pre);
}

function clearResults() {
    document.getElementById('resultsDisplay').innerHTML = 
        '<p class="placeholder">Results will appear here after running an experiment...</p>';
    startTimeGlobal = null;
    // Keep download buttons disabled until next experiment finishes
}

// ============= FILE OPERATIONS =============
async function downloadResults() {
    try {
        const response = await fetch(`${API_BASE}/download-results`);
        
        if (!response.ok) {
            throw new Error('Failed to download results');
        }

        const blob = await response.blob();
        const timestamp = new Date().toLocaleTimeString().replace(/:/g, '-');
        const filename = `results_${timestamp}.csv`;
        
        downloadBlob(blob, filename);
        log('Results downloaded successfully', 'success');
    } catch (error) {
        log(`Error downloading results: ${error.message}`, 'error');
    }
}

async function generateReport() {
    try {
        const response = await fetch(`${API_BASE}/create-report`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Failed to generate report');
        }

        const report = await response.json();
        displayReportModal(report);
        log('Report generated successfully', 'success');
    } catch (error) {
        log(`Error generating report: ${error.message}`, 'error');
    }
}

function displayReportModal(report) {
    const reportContent = document.getElementById('reportContent');
    
    const resultDisplay = typeof report.results === 'string' 
        ? `<pre style="background: #f1f5f9; padding: 1rem; border-radius: 6px; overflow: auto; max-height: 500px; font-family: Courier New, monospace; font-size: 0.85rem; line-height: 1.4;">${escapeHtml(report.results)}</pre>`
        : `<pre>${escapeHtml(JSON.stringify(report.results, null, 2))}</pre>`;
    
    const html = `
        <div class="report-data">
            <h3>📊 Experiment Report</h3>
            <p><strong>Module:</strong> ${escapeHtml(report.module || 'Batch')}</p>
            <p><strong>Status:</strong> <span style="color: ${report.status === 'completed' ? '#10b981' : '#ef4444'}; font-weight: bold;">${escapeHtml(report.status.toUpperCase())}</span></p>
            <p><strong>Report Time:</strong> ${escapeHtml(new Date(report.timestamp).toLocaleString())}</p>
            ${report.start_time ? `<p><strong>Start Time:</strong> ${escapeHtml(new Date(report.start_time).toLocaleString())}</p>` : ''}
            <hr style="margin: 1rem 0; border: 1px solid #e2e8f0;">
            <h4>📋 Results & Output:</h4>
            ${resultDisplay}
        </div>
    `;
    
    reportContent.innerHTML = html;
    document.getElementById('reportModal').classList.add('show');
}

function downloadReportAsFile() {
    const reportContent = document.getElementById('reportContent').innerText;
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `report_${timestamp}.txt`;
    
    // Get module name from the report data
    const moduleMatch = reportContent.match(/Module:\s*(\w+)/);
    const moduleName = moduleMatch ? moduleMatch[1] : 'experiment';
    
    downloadBlob(new Blob([`EXPERIMENT REPORT\n${'='.repeat(80)}\n\n${reportContent}`], {type: 'text/plain'}), `report_${moduleName}_${timestamp}.txt`);
    log('Report downloaded successfully', 'success');
}

function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ============= LOGGING =============
function log(message, level = 'info') {
    const logsContainer = document.getElementById('logsContainer');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('p');
    logEntry.className = `log-entry log-${level}`;
    logEntry.textContent = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    logsContainer.appendChild(logEntry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// ============= UTILITIES =============
function disableAllControls() {
    document.querySelectorAll('.experiment-btn, .btn-primary, .btn-secondary, #stopBtn').forEach(btn => {
        btn.disabled = true;
    });
    document.getElementById('stopBtn').disabled = false;
}

function enableAllControls() {
    document.querySelectorAll('.experiment-btn, .btn-primary, .btn-secondary').forEach(btn => {
        btn.disabled = false;
    });
    document.getElementById('stopBtn').disabled = true;
}

function resetDownloadButtons(enable) {
    document.getElementById('downloadBtn').disabled = !enable;
    document.getElementById('reportBtn').disabled = !enable;
}

function closeModal() {
    document.getElementById('reportModal').classList.remove('show');
}

function capitalizeFirst(str) {
    return str ? str[0].toUpperCase() + str.slice(1) : '';
}

function formatValue(value) {
    if (typeof value === 'number') {
        return value.toFixed(2);
    }
    return value;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

async function waitForCompletion() {
    return new Promise(resolve => {
        let lastStatus = '';
        const checkStatus = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE}/status`);
                const status = await response.json();
                
                // Only resolve when status transitions to completed/error
                // (Check if status changed from 'running' to 'completed'/'error')
                if (lastStatus === 'running' && (status.status === 'completed' || status.status === 'error')) {
                    clearInterval(checkStatus);
                    resolve();
                }
                lastStatus = status.status;
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }, 300);

        // Timeout after 10 minutes
        setTimeout(() => {
            clearInterval(checkStatus);
            resolve();
        }, 600000);
    });
}

// ============= GRAPHS SECTION =============
async function refreshGraphs() {
    try {
        document.getElementById('refreshGraphsBtn').disabled = true;
        log('Refreshing graphs...', 'info');

        const response = await fetch(`${API_BASE}/graphs`);
        if (!response.ok) {
            throw new Error('Failed to fetch graphs');
        }

        const data = await response.json();
        displayGraphs(data);
        document.getElementById('downloadGraphsBtn').disabled = false;
        log('Graphs refreshed successfully', 'success');
    } catch (error) {
        log(`Error refreshing graphs: ${error.message}`, 'error');
    } finally {
        document.getElementById('refreshGraphsBtn').disabled = false;
    }
}

function displayGraphs(graphsData) {
    const graphsContainer = document.getElementById('graphsContainer');
    const graphsGrid = graphsContainer.querySelector('.graphs-grid');
    
    // Clear existing graphs
    graphsGrid.innerHTML = '';

    if (!graphsData || Object.keys(graphsData).length === 0) {
        graphsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-light);">No graphs available yet. Run an experiment to generate graphs.</p>';
        return;
    }

    // Create graph cards for each graph
    Object.entries(graphsData).forEach(([title, imagePath]) => {
        const card = document.createElement('div');
        card.className = 'graph-card';
        card.innerHTML = `
            <img src="${imagePath}" alt="${title}" title="${title}" 
                 style="cursor: pointer;" 
                 onclick="openGraphFullscreen('${imagePath}', '${title}')">
            <div style="padding: 1rem; text-align: center; background: rgba(99, 102, 241, 0.05);">
                <h4 style="margin: 0; color: var(--text-primary);">${title}</h4>
            </div>
        `;
        graphsGrid.appendChild(card);
    });
}

function openGraphFullscreen(imagePath, title) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = imagePath;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '✕';
    closeBtn.style.cssText = `
        position: absolute;
        top: 30px;
        right: 30px;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    `;
    
    closeBtn.onmouseover = () => closeBtn.style.background = 'rgba(255, 255, 255, 0.2)';
    closeBtn.onmouseout = () => closeBtn.style.background = 'rgba(255, 255, 255, 0.1)';
    
    const close = () => {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    };
    
    closeBtn.onclick = close;
    modal.onclick = close;
    img.onclick = (e) => e.stopPropagation();
    
    modal.appendChild(img);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);
    
    modal.style.animation = 'fadeIn 0.3s ease';
}

async function downloadGraphs() {
    try {
        log('Downloading graphs...', 'info');
        const response = await fetch(`${API_BASE}/download-graphs`);
        
        if (!response.ok) {
            throw new Error('Failed to download graphs');
        }

        const blob = await response.blob();
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        downloadBlob(blob, `graphs_${timestamp}.zip`);
        log('Graphs downloaded successfully', 'success');
    } catch (error) {
        log(`Error downloading graphs: ${error.message}`, 'error');
    }
}

// Add CSS animations if not already present
if (!document.querySelector('style[data-animations]')) {
    const style = document.createElement('style');
    style.setAttribute('data-animations', 'true');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// ============= IMAGE UPLOAD SECTION =============
let selectedFiles = [];
const MAX_FILES = 5;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

function handleFiles(files) {
    selectedFiles = [];
    let validCount = 0;

    for (let file of files) {
        // Validate file type
        if (!['image/jpeg', 'image/png', 'image/gif', 'image/bmp'].includes(file.type)) {
            log(`Invalid file type: ${file.name}. Only JPG, PNG, GIF, BMP allowed.`, 'warning');
            continue;
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            log(`File too large: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB). Max 10MB.`, 'warning');
            continue;
        }

        // Validate max files
        if (validCount >= MAX_FILES) {
            log(`Maximum ${MAX_FILES} files allowed. Ignoring remaining files.`, 'warning');
            break;
        }

        selectedFiles.push(file);
        validCount++;
    }

    if (selectedFiles.length > 0) {
        displayImagePreviews();
        document.getElementById('uploadBtn').disabled = false;
        log(`${validCount} image(s) selected for upload`, 'success');
    } else {
        log('No valid images selected', 'warning');
        document.getElementById('uploadBtn').disabled = true;
    }
}

function displayImagePreviews() {
    const previewContainer = document.getElementById('uploadedImages');
    previewContainer.innerHTML = '';
    previewContainer.classList.remove('empty');

    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'image-preview';
            previewDiv.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}">
                <div class="image-preview-info">${file.name}</div>
                <button class="remove-image" onclick="removeImagePreview(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            previewContainer.appendChild(previewDiv);
        };
        
        reader.readAsDataURL(file);
    });
}

function removeImagePreview(index) {
    selectedFiles.splice(index, 1);
    if (selectedFiles.length === 0) {
        document.getElementById('uploadBtn').disabled = true;
        document.getElementById('uploadedImages').classList.add('empty');
    }
    displayImagePreviews();
}

function clearUploadArea() {
    selectedFiles = [];
    document.getElementById('uploadedImages').innerHTML = '';
    document.getElementById('uploadedImages').classList.add('empty');
    document.getElementById('imageInput').value = '';
    document.getElementById('uploadBtn').disabled = true;
    log('Upload area cleared', 'info');
}

async function uploadImages() {
    if (selectedFiles.length === 0) {
        log('No images selected', 'warning');
        return;
    }

    try {
        document.getElementById('uploadBtn').disabled = true;
        log(`Uploading ${selectedFiles.length} image(s)...`, 'info');

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('images', file);
        });

        const response = await fetch(`${API_BASE}/upload-images`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        const result = await response.json();
        
        log(`Successfully uploaded ${result.uploaded} image(s)`, 'success');
        
        if (result.uploaded > 0) {
            clearUploadArea();
            // Load and display output images
            loadOutputImages();
            log('Images saved to output folder', 'success');
        }

    } catch (error) {
        log(`Error uploading images: ${error.message}`, 'error');
    } finally {
        document.getElementById('uploadBtn').disabled = selectedFiles.length === 0;
    }
}

// ============= VALIDATION FUNCTIONS =============
function showValidationMessage(message, type = 'error') {
    const controlPanel = document.querySelector('.control-panel');
    
    // Remove existing message
    const existingMsg = controlPanel.querySelector('.form-validation-msg');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Create new message
    const msgDiv = document.createElement('div');
    msgDiv.className = `form-validation-msg ${type}`;
    
    const icon = type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    msgDiv.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    controlPanel.insertBefore(msgDiv, controlPanel.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        msgDiv.style.animation = 'slideDown 0.3s ease-out reverse';
        setTimeout(() => msgDiv.remove(), 300);
    }, 5000);
}

// ============= PROCESSING STATUS FUNCTIONS =============
function showProcessingStatus(moduleName) {
    const progressSection = document.querySelector('.progress-section');
    
    // Remove existing status if any
    const existingStatus = progressSection.querySelector('.processing-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Create new status
    const statusDiv = document.createElement('div');
    statusDiv.className = 'processing-status';
    statusDiv.innerHTML = `
        <div class="processing-spinner"></div>
        <div class="processing-text">
            Processing images with <span class="module-name">${moduleName}</span> module...
        </div>
    `;
    
    progressSection.insertBefore(statusDiv, progressSection.firstChild);
}

function hideProcessingStatus() {
    const statusDiv = document.querySelector('.processing-status');
    if (statusDiv) {
        statusDiv.style.animation = 'slideDown 0.3s ease-out reverse';
        setTimeout(() => statusDiv.remove(), 300);
    }
}

// ============= OUTPUT IMAGES FUNCTIONS =============
async function loadOutputImages() {
    try {
        // List all output images from the server with cache-busting parameter
        const cacheBuster = new Date().getTime();
        const response = await fetch(`${API_BASE}/list-output-images?t=${cacheBuster}`, {
            cache: 'no-store'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch output images');
        }
        
        const data = await response.json();
        displayOutputImages(data.images || []);
        
    } catch (error) {
        console.error('Error loading output images:', error);
        log(`Could not load output images: ${error.message}`, 'warning');
    }
}

function displayOutputImages(images) {
    const grid = document.getElementById('outputImagesGrid');
    
    if (!images || images.length === 0) {
        grid.innerHTML = '<p class="empty-state">No processed images available yet.</p>';
        grid.classList.add('empty');
        return;
    }
    
    // Filter to show only processed images (those starting with "output_")
    const processedImages = images.filter(imagePath => {
        const fileName = imagePath.split('/').pop() || imagePath;
        return fileName.startsWith('output_');
    });
    
    if (processedImages.length === 0) {
        grid.innerHTML = '<p class="empty-state">No processed images available yet. Run an experiment to generate grayscale outputs.</p>';
        grid.classList.add('empty');
        return;
    }
    
    grid.innerHTML = '';
    grid.classList.remove('empty');
    
    // Show all processed images
    processedImages.forEach(imagePath => {
        const fileName = imagePath.split('/').pop() || imagePath;
        
        const card = document.createElement('div');
        card.className = 'output-image-card';
        card.innerHTML = `
            <img src="${imagePath}" alt="${fileName}" />
            <div class="output-image-overlay">
                <button class="image-action-btn" title="View full size" onclick="openFullscreenImage('${imagePath}', '${fileName}')">
                    <i class="fas fa-expand"></i>
                </button>
                <button class="image-action-btn" title="Download" onclick="downloadImage('${imagePath}', '${fileName}')">
                    <i class="fas fa-download"></i>
                </button>
            </div>
            <div class="output-image-info">${fileName}</div>
        `;
        
        grid.appendChild(card);
    });
}

function openFullscreenImage(imagePath, fileName) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.95);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: pointer;
        animation: fadeIn 0.3s ease;
    `;
    
    const img = document.createElement('img');
    img.src = imagePath;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '✕';
    closeBtn.style.cssText = `
        position: absolute;
        top: 30px;
        right: 30px;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 10001;
    `;
    
    closeBtn.onmouseover = () => closeBtn.style.background = 'rgba(255, 255, 255, 0.2)';
    closeBtn.onmouseout = () => closeBtn.style.background = 'rgba(255, 255, 255, 0.1)';
    
    const close = () => {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    };
    
    closeBtn.onclick = close;
    modal.onclick = close;
    img.onclick = (e) => e.stopPropagation();
    
    modal.appendChild(img);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);
}

function downloadImage(imagePath, fileName) {
    const a = document.createElement('a');
    a.href = imagePath;
    a.download = fileName || 'image.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    log(`Downloading ${fileName}...`, 'success');
}

function initializeCollapsibleOutputImages() {
    const header = document.getElementById('outputImagesHeader');
    const content = document.getElementById('outputImagesContent');
    const toggleBtn = document.getElementById('toggleOutputImages');
    
    if (!header) return;
    
    header.addEventListener('click', () => {
        content.classList.toggle('collapsed');
        toggleBtn.classList.toggle('collapsed');
    });
}

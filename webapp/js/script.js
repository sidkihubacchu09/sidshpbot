const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse incoming payloads
app.use(express.json());

// Serve static frontend files automatically from the /public folder
app.use(express.static(path.join(__dirname, 'public')));

// Create a physical directory to house the running python files
const SCRIPTS_DIR = path.join(__dirname, 'running_nodes');
if (!fs.existsSync(SCRIPTS_DIR)) {
    fs.mkdirSync(SCRIPTS_DIR);
}

// Global runtime tracking matrix mapping live process nodes
const activeWorkers = new Map();

// ==========================================
// API Endpoint: Deploy & Write Script to Disk
// ==========================================
app.post('/api/deploy', (req, res) => {
    const { fileName, scriptSource } = req.body;
    if (!fileName || !scriptSource) {
        return res.status(400).json({ error: 'Missing code payload properties.' });
    }

    try {
        const safeFileName = path.basename(fileName);
        const filePath = path.join(SCRIPTS_DIR, safeFileName);
        
        // Write the real Python file code onto the machine storage system
        fs.writeFileSync(filePath, scriptSource, 'utf8');
        
        res.json({ success: true, message: 'Script integrated successfully.', filePath });
    } catch (err) {
        res.status(500).json({ error: `Disk write fault: ${err.message}` });
    }
});

// ==========================================
// API Endpoint: Launch Real Python Execution Process
// ==========================================
app.post('/api/start', (req, res) => {
    const { botId, fileName } = req.body;
    const safeFileName = path.basename(fileName);
    const filePath = path.join(SCRIPTS_DIR, safeFileName);

    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Source file not found on execution layer.' });
    }

    if (activeWorkers.has(botId)) {
        return res.json({ message: 'Worker node already active.', status: 'Running' });
    }

    // Spawn a real asynchronous Python runtime sub-process on the local OS
    const processInstance = spawn('python3', [filePath], {
        env: { ...process.env, PYTHONUNBUFFERED: '1' } // Forces output to stream instantly without caching
    });

    const processLogs = [`[SYS] Worker environment mapped cleanly. Spawning Python interpreter...`];
    
    activeWorkers.set(botId, {
        process: processInstance,
        logs: processLogs,
        startTime: Date.now()
    });

    // Hook into real Python stdout stream channel
    processInstance.stdout.on('data', (data) => {
        const line = data.toString().trim();
        if (line) processLogs.push(`[STDOUT] ${line}`);
    });

    // Hook into real Python runtime errors / stderr channel
    processInstance.stderr.on('data', (data) => {
        const line = data.toString().trim();
        if (line) processLogs.push(`[STDERR] ${line}`);
    });

    // Clean up registry space instantly when execution completes
    processInstance.on('close', (code) => {
        processLogs.push(`[SYS-TERMINATION] Process exited with exit status code: ${code}`);
        activeWorkers.delete(botId);
    });

    res.json({ success: true, status: 'Running' });
});

// ==========================================
// API Endpoint: Pull Active Stream Diagnostic Logs
// ==========================================
app.get('/api/logs/:botId', (req, res) => {
    const worker = activeWorkers.get(req.params.botId);
    if (!worker) {
        return res.json({ active: false, logs: ['[OFFLINE] Process infrastructure idle. Start execution runtime to reactivate loop stream.'] });
    }
    res.json({ active: true, logs: worker.logs, startTime: worker.startTime });
});

// ==========================================
// API Endpoint: Core SIGTERM Lifecyle Termination
// ==========================================
app.post('/api/stop', (req, res) => {
    const { botId } = req.body;
    const worker = activeWorkers.get(botId);

    if (worker) {
        worker.process.kill('SIGTERM'); // Interrupt and end the active script task loop execution
        activeWorkers.delete(botId);
        return res.json({ success: true, message: 'SIGTERM lifecycle signal issued.' });
    }
    res.json({ message: 'Process was not actively allocated.' });
});

app.listen(PORT, () => {
    console.log(`====================================================`);
    console.log(`🚀 HOUSING SERVER RUNNING ACTIVE ON PORT: ${PORT}`);
    console.log(`🔗 Local Access URL: http://localhost:${PORT}`);
    console.log(`====================================================`);
});

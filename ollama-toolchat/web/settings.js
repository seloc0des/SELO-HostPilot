let readRoots = [];
let writeRoots = [];

async function loadSettings() {
    try {
        const response = await fetch('/v1/settings');
        if (!response.ok) {
            throw new Error('Failed to load settings');
        }
        
        const data = await response.json();
        
        // Populate form fields
        document.getElementById('ollamaUrl').value = data.ollama_url;
        document.getElementById('ollamaModel').value = data.ollama_model;
        document.getElementById('sandboxMode').value = data.sandbox_mode;
        document.getElementById('allowNetwork').checked = data.allow_network;
        document.getElementById('logLevel').value = data.log_level;
        
        // Load paths
        readRoots = data.read_roots || [];
        writeRoots = data.write_roots || [];
        
        renderReadRoots();
        renderWriteRoots();
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showAlert('Failed to load settings: ' + error.message, 'error');
    }
}

function renderReadRoots() {
    const container = document.getElementById('readRootsList');
    container.innerHTML = '';
    
    readRoots.forEach((path, index) => {
        const div = document.createElement('div');
        div.className = 'path-item';
        div.innerHTML = `
            <input type="text" value="${path}" onchange="updateReadRoot(${index}, this.value)">
            <button type="button" onclick="removeReadRoot(${index})">Remove</button>
        `;
        container.appendChild(div);
    });
    
    if (readRoots.length === 0) {
        const div = document.createElement('div');
        div.className = 'help-text';
        div.textContent = 'No read paths configured. Click "Add Path" to add one.';
        container.appendChild(div);
    }
}

function renderWriteRoots() {
    const container = document.getElementById('writeRootsList');
    container.innerHTML = '';
    
    writeRoots.forEach((path, index) => {
        const div = document.createElement('div');
        div.className = 'path-item';
        div.innerHTML = `
            <input type="text" value="${path}" onchange="updateWriteRoot(${index}, this.value)">
            <button type="button" onclick="removeWriteRoot(${index})">Remove</button>
        `;
        container.appendChild(div);
    });
    
    if (writeRoots.length === 0) {
        const div = document.createElement('div');
        div.className = 'help-text';
        div.textContent = 'No write paths configured. Click "Add Path" to add one.';
        container.appendChild(div);
    }
}

function addReadRoot() {
    readRoots.push('/home');
    renderReadRoots();
}

function removeReadRoot(index) {
    readRoots.splice(index, 1);
    renderReadRoots();
}

function updateReadRoot(index, value) {
    readRoots[index] = value;
}

function addWriteRoot() {
    writeRoots.push('/home');
    renderWriteRoots();
}

function removeWriteRoot(index) {
    writeRoots.splice(index, 1);
    renderWriteRoots();
}

function updateWriteRoot(index, value) {
    writeRoots[index] = value;
}

function showAlert(message, type = 'success') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

document.getElementById('settingsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const saveBtn = document.getElementById('saveBtn');
    const originalText = saveBtn.textContent;
    saveBtn.innerHTML = '<span class="loading"></span> Saving...';
    saveBtn.disabled = true;
    
    try {
        const formData = {
            ollama_url: document.getElementById('ollamaUrl').value,
            ollama_model: document.getElementById('ollamaModel').value,
            read_roots: readRoots.filter(p => p.trim()),
            write_roots: writeRoots.filter(p => p.trim()),
            sandbox_mode: document.getElementById('sandboxMode').value,
            allow_network: document.getElementById('allowNetwork').checked,
            log_level: document.getElementById('logLevel').value,
        };
        
        const response = await fetch('/v1/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save settings');
        }
        
        const result = await response.json();
        showAlert(result.message, 'success');
        
        if (result.restart_required) {
            showAlert('⚠️ Please restart the application for changes to take effect.', 'warning');
        }
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showAlert('Failed to save settings: ' + error.message, 'error');
    } finally {
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    }
});

// Load settings on page load
loadSettings();

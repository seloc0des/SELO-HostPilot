let sessionId = null;
let pendingPlanId = null;

const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const modelSelect = document.getElementById('modelSelect');
const streamingClient = new StreamingChatClient();

function addMessage(role, content, planId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const formattedContent = formatMessage(content);
    contentDiv.innerHTML = formattedContent;
    
    messageDiv.appendChild(contentDiv);
    
    if (planId) {
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'confirmation-buttons';
        
        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'btn-confirm';
        confirmBtn.textContent = 'Confirm';
        confirmBtn.onclick = () => confirmAction(planId, true);
        
        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn-cancel';
        cancelBtn.textContent = 'Cancel';
        cancelBtn.onclick = () => confirmAction(planId, false);
        
        buttonsDiv.appendChild(confirmBtn);
        buttonsDiv.appendChild(cancelBtn);
        contentDiv.appendChild(buttonsDiv);
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatMessage(content) {
    content = content.replace(/&/g, '&amp;')
                     .replace(/</g, '&lt;')
                     .replace(/>/g, '&gt;');
    
    content = content.replace(/\n/g, '<br>');
    
    content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    return content;
}

function setLoading(loading) {
    sendButton.disabled = loading;
    messageInput.disabled = loading;
    
    if (loading) {
        sendButton.innerHTML = '<span class="loading"></span>';
    } else {
        sendButton.textContent = 'Send';
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    addMessage('user', message);
    messageInput.value = '';
    setLoading(true);
    
    try {
        await sendMessageStreaming(message);
    } catch (error) {
        console.error('Error:', error);
        addMessage('system', `Error: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

async function sendMessageStreaming(message) {
    let statusMessage = null;
    
    await streamingClient.sendMessageStreaming(sessionId, message, (event) => {
        switch (event.type) {
            case 'session':
                sessionId = event.session_id;
                break;
            
            case 'status':
                if (statusMessage) {
                    statusMessage.textContent = event.message;
                } else {
                    statusMessage = addStatusMessage(event.message);
                }
                break;
            
            case 'tool_call':
                if (statusMessage) {
                    statusMessage.remove();
                    statusMessage = null;
                }
                // More assistant-like message instead of technical tool name
                addMessage('system', `💭 ${event.explain}...`);
                break;
            
            case 'tool_result':
                // Tool result is handled internally, just show completion
                break;
            
            case 'confirmation':
                if (statusMessage) {
                    statusMessage.remove();
                    statusMessage = null;
                }
                pendingPlanId = event.plan_id;
                addMessage('assistant', event.message, event.plan_id);
                break;
            
            case 'message':
                if (statusMessage) {
                    statusMessage.remove();
                    statusMessage = null;
                }
                addMessage(event.role, event.content);
                break;
            
            case 'done':
                if (statusMessage) {
                    statusMessage.remove();
                    statusMessage = null;
                }
                break;
            
            case 'error':
                if (statusMessage) {
                    statusMessage.remove();
                    statusMessage = null;
                }
                addMessage('system', `Error: ${event.message}`);
                break;
        }
    });
}

function addStatusMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.id = 'streaming-status';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<em>${text}</em>`;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return contentDiv;
}

async function confirmAction(planId, confirm) {
    setLoading(true);
    
    try {
        const response = await fetch('/v1/chat/confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                plan_id: planId,
                confirm: confirm,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        addMessage('assistant', data.reply);
        pendingPlanId = null;
    } catch (error) {
        console.error('Error:', error);
        addMessage('system', `Error: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

modelSelect.addEventListener('change', async (e) => {
    const newModel = e.target.value;
    
    try {
        const response = await fetch('/v1/model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: newModel,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to change model');
        }
        
        const data = await response.json();
        addMessage('system', `✓ ${data.message}`);
    } catch (error) {
        console.error('Error changing model:', error);
        addMessage('system', `Error changing model: ${error.message}`);
        loadCurrentModel();
    }
});

async function loadAvailableModels() {
    try {
        const response = await fetch('/v1/models');
        if (response.ok) {
            const data = await response.json();
            modelSelect.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            
            await loadCurrentModel();
        } else {
            console.error('Failed to load models');
            modelSelect.innerHTML = '<option value="">Failed to load models</option>';
        }
    } catch (error) {
        console.error('Error loading available models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
    }
}

async function loadCurrentModel() {
    try {
        const response = await fetch('/v1/model');
        if (response.ok) {
            const data = await response.json();
            modelSelect.value = data.model;
        }
    } catch (error) {
        console.error('Error loading current model:', error);
    }
}

loadAvailableModels();
messageInput.focus();

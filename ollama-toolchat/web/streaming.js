// Streaming support for Server-Sent Events (SSE)

class StreamingChatClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    async sendMessageStreaming(sessionId, message, onEvent) {
        const response = await fetch(`${this.baseUrl}/v1/chat/send/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            
            // Process complete SSE messages
            const lines = buffer.split('\n\n');
            buffer = lines.pop(); // Keep incomplete message in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    try {
                        const event = JSON.parse(data);
                        onEvent(event);
                        
                        if (event.type === 'done' || event.type === 'error') {
                            return;
                        }
                    } catch (e) {
                        console.error('Failed to parse SSE data:', e);
                    }
                }
            }
        }
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StreamingChatClient;
}

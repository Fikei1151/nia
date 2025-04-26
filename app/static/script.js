document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Keep track of the thread ID
    let threadId = 'new';
    
    // Function to add messages to the chat
    function addMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        messageDiv.textContent = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Function to show the typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('typing-indicator');
        indicator.id = 'typingIndicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            indicator.appendChild(dot);
        }
        
        chatBox.appendChild(indicator);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    
    // Function to remove the typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Send message to the API
    async function sendMessage(message) {
        // Show typing indicator while waiting for response
        showTypingIndicator();
        
        try {
            const response = await fetch(`/api/v1/chat/${threadId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    platform: 'web',
                    user_id: 'web_user',
                    project_id: 'nia_chat'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Save the thread ID for future messages
            threadId = data.thread_id;
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add the AI's response to the chat
            addMessage(data.reply, 'bot');
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessage('Sorry, something went wrong. Please try again.', 'system');
        }
    }
    
    // Handle send button click
    sendBtn.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            userInput.value = '';
            sendMessage(message);
        }
    });
    
    // Also send when pressing Enter (but Shift+Enter allows new lines)
    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendBtn.click();
        }
    });
}); 
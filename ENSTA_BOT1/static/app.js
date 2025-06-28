// 1. Sync URL token to localStorage FIRST
const urlParams = new URLSearchParams(window.location.search);
const urlToken = urlParams.get('token');
if (urlToken) {
    localStorage.setItem('authToken', urlToken);
    window.history.replaceState({}, '', '/chatbot'); // Remove token from URL
    console.log("Token saved from URL");
}

// 2. Initialize chatbox if authenticated
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('authToken');
    console.log("Initial token check:", token);  // Debug
    
    if (token) {
        new Chatbox();  // Start chat
    } else {
        console.log("No token - redirecting");
        window.location.href = 'http://localhost:8901';
    }
});
class Chatbox {
    constructor() {
        this.args = {
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.messages = [];
        this.initializeChatbox();
    }

    initializeChatbox() {
        const { chatBox, sendButton } = this.args;
        chatBox.classList.add('chatbox--active');

        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value;
        if (text1 === "") return;
    
        // Show user message immediately
        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);
        this.updateChatText(chatbox);
        textField.value = '';

        // Send message to backend for saving (save-message API)
        const userId = "123"; // Use actual userId from authToken or localStorage if needed
        const sender = "user";

       fetch('http://localhost:5000/save-message', {
        method: 'POST',
        body: JSON.stringify({ userId, sender, message: text1 }),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    
        // Fetch bot response with token
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}` //  CRITICAL ADDITION
            },
        })
        .then(response => {
            if (response.status === 401) throw new Error('Unauthorized'); //  ADDED
            return response.json();
        })
        .then(r => {
            let msg2 = { name: "Enstabot", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox);
        })
        .catch((error) => {
            console.error('Error:', error);
            if (error.message.includes('Unauthorized')) { //  ADDED
                localStorage.removeItem('authToken');
                window.location.href = 'http://localhost:8901';
            } else {
                let errorMsg = { 
                    name: "Enstabot", 
                    message: "Sorry, I couldn't process your request." 
                };
                this.messages.push(errorMsg);
                this.updateChatText(chatbox);
            }
        });
    }

    updateChatText(chatbox) {
        var html = '';
        // Changed: No more reverse() - messages appear in natural order
        this.messages.forEach(function(item) {
            if (item.name === "Enstabot") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>';
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            }
        });

        const chatMessage = chatbox.querySelector('.chatbox__messages');
        chatMessage.innerHTML = html;
        chatMessage.scrollTop = chatMessage.scrollHeight; // Auto-scroll to bottom
    }
}

const chatbox = new Chatbox();
import os
import re

files = [
    'index.html',
    'pasto-deportivo.html',
    'jardines.html',
    'insumos.html',
    'calculadora.html',
    'contacto.html'
]

new_script = """    <!-- Chatbot Logic -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chatbotButton = document.getElementById('chatbot-button');
            const chatbotWindow = document.getElementById('chatbot-window');
            const closeChatbot = document.getElementById('close-chatbot');
            const chatForm = document.getElementById('chat-form');
            const chatInput = document.getElementById('chat-input');
            const chatBody = chatbotWindow ? chatbotWindow.querySelector('.overflow-y-auto') : null;

            if (!chatbotButton || !chatbotWindow || !chatBody) return;

            // Generar o recuperar sessionId para el estado del chat
            let sessionId = localStorage.getItem('chatSessionId');
            if (!sessionId) {
                sessionId = "sess_" + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('chatSessionId', sessionId);
            }

            // Restore Chat State from sessionStorage
            const isChatOpen = sessionStorage.getItem('chatIsOpen') === 'true';
            if (isChatOpen) {
                chatbotWindow.classList.remove('hidden');
            }

            // Restore Chat History
            const chatHistory = sessionStorage.getItem('chatHistory');
            if (chatHistory) {
                chatBody.innerHTML = chatHistory;
            }

            // Scroll to bottom on load
            chatBody.scrollTop = chatBody.scrollHeight;

            function saveChatState() {
                sessionStorage.setItem('chatIsOpen', !chatbotWindow.classList.contains('hidden'));
            }

            function saveChatHistory() {
                sessionStorage.setItem('chatHistory', chatBody.innerHTML);
            }

            chatbotButton.addEventListener('click', () => {
                chatbotWindow.classList.toggle('hidden');
                saveChatState();
                if (!chatbotWindow.classList.contains('hidden')) {
                    chatInput.focus();
                }
            });

            closeChatbot.addEventListener('click', () => {
                chatbotWindow.classList.add('hidden');
                saveChatState();
            });

            function addMessage(msg, isUser = false) {
                const avatar = isUser ? "" : `<img src="chatbot-avatar.png" alt="Queno" class="w-8 h-8 rounded-full object-cover mt-1 shrink-0">`;
                const innerClasses = isUser
                    ? "bg-primary p-3 rounded-2xl rounded-tr-none shadow-sm text-sm text-white"
                    : "bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700 dark:text-slate-200 border border-slate-100 dark:border-slate-600";
                const wrapperClass = isUser ? "flex gap-3 mb-4 justify-end" : "flex gap-3 mb-4";

                const msgHtml = `
                    <div class="${wrapperClass}">
                        ${!isUser ? avatar : ""}
                        <div class="${innerClasses}">
                            ${msg}
                        </div>
                    </div>
                `;
                chatBody.insertAdjacentHTML('beforeend', msgHtml);
                chatBody.scrollTop = chatBody.scrollHeight;
                saveChatHistory();
            }

            function addLoader() {
                const loaderId = "loader-" + Date.now();
                const loaderHtml = `
                    <div id="${loaderId}" class="flex gap-3 mb-4">
                        <img src="chatbot-avatar.png" alt="Queno" class="w-8 h-8 rounded-full object-cover mt-1 shrink-0">
                        <div class="bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm border border-slate-100 dark:border-slate-600 flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.1s"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.2s"></span>
                        </div>
                    </div>
                `;
                chatBody.insertAdjacentHTML('beforeend', loaderHtml);
                chatBody.scrollTop = chatBody.scrollHeight;
                saveChatHistory();
                return loaderId;
            }

            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const message = chatInput.value.trim();
                if (!message) return;

                chatInput.disabled = true;
                addMessage(message, true);
                chatInput.value = '';
                const loaderId = addLoader();

                try {
                    // URL COMPLETA DE TU WEBHOOK (Cambia solo si reinicias ngrok)
                    const response = await fetch('https://marhta-unstubborn-minnie.ngrok-free.dev/webhook/8ba2c0b4-bb98-4437-b34d-4da692c16ed7', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            chatInput: message,
                            sessionId: sessionId,
                            action: "sendMessage"
                        })
                    });

                    const data = await response.json();
                    
                    const loaderEl = document.getElementById(loaderId);
                    if (loaderEl) {
                        loaderEl.remove();
                        saveChatHistory();
                    }

                    // Ajuste para leer la respuesta de n8n correctamente
                    let botReply = "Lo siento, hubo un problema al procesar la respuesta.";

                    if (Array.isArray(data)) {
                        botReply = data[0].output || data[0].text || botReply;
                    } else {
                        botReply = data.output || data.text || data.message || botReply;
                    }

                    addMessage(botReply, false);

                } catch (error) {
                    console.error("Error connecting to n8n:", error);
                    const loaderEl = document.getElementById(loaderId);
                    if (loaderEl) {
                        loaderEl.remove();
                        saveChatHistory();
                    }
                    addMessage("No pude conectar con el servidor. Revisa que ngrok y n8n estén activos.", false);
                } finally {
                    chatInput.disabled = false;
                    chatInput.focus();
                }
            });
        });
    </script>"""

for fn in files:
    with open(fn, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to replace the script block containing 'chatbotButton' 
    # and 'document.addEventListener('DOMContentLoaded', () => {' 
    # up to '</script>'
    
    # Using regex to find the target script block
    target_pattern = r'(\s*<!--\s*Chatbot Logic\s*-->\s*)?<script>\s*document\.addEventListener\(\'DOMContentLoaded\',\s*\(\)\s*=>\s*\{\s*const chatbotButton = document\.getElementById\(\'chatbot-button\'\);(.|\n)*?\}\);\s*</script>'
    
    new_content = re.sub(target_pattern, new_script, content)
    
    if new_content != content:
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {fn}")
    else:
        print(f"No changes in {fn}")

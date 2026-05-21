const fs = require('fs');
const path = require('path');
const glob = require('glob');

const newScript = `    <!-- N8N Integration snippet -->
    <script>
        // Inicializa el widget nativo de n8n si deciden incluir la librería externa
        if (window.n8nChat && typeof window.n8nChat.init === 'function') {
             window.n8nChat.init({
                 serverUrl: "http://localhost:5678"
             });
        }
    </script>

    <!-- Chatbot Logic -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chatbotButton = document.getElementById('chatbot-button');
            const chatbotWindow = document.getElementById('chatbot-window');
            const closeChatbot = document.getElementById('close-chatbot');
            const chatForm = document.getElementById('chat-form');
            const chatInput = document.getElementById('chat-input');
            const chatBody = chatbotWindow.querySelector('.overflow-y-auto');
            const submitBtn = chatForm ? chatForm.querySelector('button[type="submit"]') : null;
            
            // Generar o recuperar sessionId para el estado del chat
            let sessionId = localStorage.getItem('chatSessionId');
            if (!sessionId) {
                sessionId = "sess_" + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('chatSessionId', sessionId);
            }

            if (chatbotButton && chatbotWindow) {
                chatbotButton.addEventListener('click', () => {
                    chatbotWindow.classList.toggle('hidden');
                    if (!chatbotWindow.classList.contains('hidden')) {
                        chatInput.focus();
                    }
                });

                closeChatbot.addEventListener('click', () => {
                    chatbotWindow.classList.add('hidden');
                });

                function addMessage(msg, isUser=false) {
                    const avatar = isUser ? "" : \`<img src="chatbot-avatar.png" alt="Queno" class="w-8 h-8 rounded-full object-cover mt-1 shrink-0">\`;
                    const innerClasses = isUser 
                        ? "bg-primary p-3 rounded-2xl rounded-tr-none shadow-sm text-sm text-white" 
                        : "bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700 dark:text-slate-200 border border-slate-100 dark:border-slate-600";
                    const wrapperClass = isUser ? "flex gap-3 mb-4 justify-end" : "flex gap-3 mb-4";
                    
                    const msgHtml = \`
                        <div class="\${wrapperClass}">
                            \${!isUser ? avatar : ""}
                            <div class="\${innerClasses}">
                                \${msg}
                            </div>
                        </div>
                    \`;
                    chatBody.insertAdjacentHTML('beforeend', msgHtml);
                    chatBody.scrollTop = chatBody.scrollHeight;
                }

                function addLoader() {
                    const loaderId = "loader-" + Date.now();
                    const loaderHtml = \`
                        <div id="\${loaderId}" class="flex gap-3 mb-4">
                            <img src="chatbot-avatar.png" alt="Queno" class="w-8 h-8 rounded-full object-cover mt-1 shrink-0">
                            <div class="bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm border border-slate-100 dark:border-slate-600 flex items-center gap-1">
                                <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
                                <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.1s"></span>
                                <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.2s"></span>
                            </div>
                        </div>
                    \`;
                    chatBody.insertAdjacentHTML('beforeend', loaderHtml);
                    chatBody.scrollTop = chatBody.scrollHeight;
                    return loaderId;
                }

                chatForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const message = chatInput.value.trim();
                    if (!message) return;

                    // Bloquear inhabilitar
                    chatInput.disabled = true;
                    if(submitBtn) {
                        submitBtn.disabled = true;
                        submitBtn.classList.add('opacity-50');
                    }

                    // Añadir mensaje de usuario
                    addMessage(message, true);
                    chatInput.value = '';
                    
                    // Mostrar loader visual
                    const loaderId = addLoader();

                    try {
                        // Conectar con el flujo n8n
                        const response = await fetch('http://localhost:5678/webhook/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ chatInput: message, sessionId: sessionId })
                        });

                        const data = await response.json();
                        
                        // Eliminar loader
                        document.getElementById(loaderId)?.remove();

                        // Manejar la respuesta del servidor n8n (tomamos output o text según formatee tu n8n)
                        const botReply = data.output || data.text || data.message || (Array.isArray(data) ? data[0].output : "Lo siento, no pude procesar tu solicitud.");
                        addMessage(botReply, false);
                        
                    } catch (error) {
                        console.error("Error connecting to n8n:", error);
                        document.getElementById(loaderId)?.remove();
                        addMessage("Ocurrió un error al contactar al asistente. Asegúrate de que n8n esté corriendo en http://localhost:5678", false);
                    } finally {
                        chatInput.disabled = false;
                        if(submitBtn) {
                            submitBtn.disabled = false;
                            submitBtn.classList.remove('opacity-50');
                        }
                        chatInput.focus();
                    }
                });
            }
        });
    </script>
</body>`;

const files = ['index.html', 'contacto.html', 'insumos.html', 'jardines.html', 'pasto-deportivo.html', 'calculadora.html'];

files.forEach(file => {
    try {
        let content = fs.readFileSync(file, 'utf8');
        let regex = /<!-- Chatbot Logic -->[\s\S]*?<\/script>\s*<\/body>/;

        if (regex.test(content)) {
            let newContent = content.replace(regex, newScript);
            fs.writeFileSync(file, newContent, 'utf8');
            console.log(`Updated ${file}`);
        } else {
            console.log(`Could not find regex pattern in ${file}`);
        }
    } catch (e) {
        console.log(`Skipped ${file}: ${e.message}`);
    }
});

import os
import glob
import re

new_chatbot_snippet = """    <!-- Chatbot Widget -->
    <div id="chatbot-widget" class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
        <!-- Chat Window (Hidden by default) -->
        <div id="chatbot-window"
            class="hidden w-80 md:w-96 h-[500px] max-h-[80vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-primary/20 flex flex-col overflow-hidden transition-all duration-300 origin-bottom-right">
            <!-- Header -->
            <div class="bg-primary p-4 flex items-center justify-between text-white">
                <div class="flex items-center gap-3">
                    <div class="relative">
                        <img src="chatbot-avatar.png" alt=" Queno"
                            class="w-10 h-10 rounded-full object-cover border-2 border-white/20">
                        <span
                            class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-primary rounded-full"></span>
                    </div>
                    <div>
                        <h3 class="font-bold text-sm">Queno</h3>
                        <p class="text-xs text-white/80">En línea</p>
                    </div>
                </div>
                <button id="close-chatbot" class="text-white/80 hover:text-white transition-colors">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <!-- Chat Body -->
            <div id="chat-body" class="flex-1 p-4 bg-slate-50 dark:bg-slate-800 overflow-y-auto">
                <div class="text-center text-xs text-slate-400 mb-4">Hoy</div>
                <div class="flex gap-3 mb-4">
                    <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm mt-1 shrink-0">Q</div>
                    <div
                        class="bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700 dark:text-slate-200 border border-slate-100 dark:border-slate-600">
                        ¡Hola! Soy Queno, tu asesor experto en césped sintético. ¿En qué puedo ayudarte hoy para
                        transformar tu espacio?
                    </div>
                </div>
            </div>
            <!-- Chat Input (Ready for n8n) -->
            <div class="p-3 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
                <form id="chat-form" class="flex items-center gap-2">
                    <input type="text" id="chat-input" placeholder="Escribe tu mensaje..."
                        class="flex-1 bg-slate-100 dark:bg-slate-800 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 dark:text-white"
                        required>
                    <button type="submit" id="chat-submit-btn"
                        class="bg-primary text-white p-2 rounded-full w-9 h-9 flex items-center justify-center hover:bg-primary/90 transition-colors">
                        <span class="material-symbols-outlined text-sm">send</span>
                    </button>
                </form>
            </div>
        </div>

        <!-- Chat Button -->
        <button id="chatbot-button"
            class="relative group flex items-center justify-center w-[76px] h-[76px] rounded-full bg-white dark:bg-slate-800 shadow-xl border-2 border-primary hover:scale-105 transition-transform duration-300">
            <div class="w-full h-full rounded-full bg-primary text-white flex items-center justify-center font-bold text-3xl">Q</div>
            <span
                class="absolute -top-1 -right-1 w-5 h-5 bg-green-500 border-[3px] border-white dark:border-slate-800 rounded-full"></span>
            <div
                class="absolute right-full mr-4 bg-black/80 text-white text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                ¿Necesitas ayuda?
            </div>
        </button>
    </div>

    <!-- N8N Integration snippet -->
    <script>
        // Si tienes el script oficial inyectable cargado en tu html, esto lo inicializaría.
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
            const chatBody = document.getElementById('chat-body');
            const submitBtn = document.getElementById('chat-submit-btn');
            
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
                    const avatar = isUser ? "" : `<div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm mt-1 shrink-0">Q</div>`;
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
                }

                function addLoader() {
                    const loaderId = "loader-" + Date.now();
                    const loaderHtml = `
                        <div id="${loaderId}" class="flex gap-3 mb-4">
                            <div class="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold text-sm mt-1 shrink-0">Q</div>
                            <div class="bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm border border-slate-100 dark:border-slate-600 flex items-center gap-1">
                                <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
                                <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.1s"></span>
                                <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.2s"></span>
                            </div>
                        </div>
                    `;
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
                    submitBtn.disabled = true;
                    submitBtn.classList.add('opacity-50');

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
                        addMessage("Ocurrió un error al contactar con el asistente n8n. Por favor, asegúrate de que el flujo local está activo (http://localhost:5678).", false);
                    } finally {
                        chatInput.disabled = false;
                        submitBtn.disabled = false;
                        submitBtn.classList.remove('opacity-50');
                        chatInput.focus();
                    }
                });
            }
        });
    </script>
</body>"""

for file_path in glob.glob("*.html"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Buscar el inicio del widget y cortarlo hasta el cierre del body
    pattern = re.compile(r'<!-- Chatbot Widget -->.*?</body>', re.DOTALL)
    
    if pattern.search(content):
        # Reemplazar con el nuevo
        new_content = pattern.sub(new_chatbot_snippet, content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated chatbot in {file_path}")
    else:
        print(f"Could not find Chatbot Widget in {file_path}")

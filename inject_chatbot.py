import os
import glob

html_snippet = """
    <!-- Chatbot Widget -->
    <div id="chatbot-widget" class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
        <!-- Chat Window (Hidden by default) -->
        <div id="chatbot-window" class="hidden w-80 md:w-96 h-[500px] max-h-[80vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-primary/20 flex flex-col overflow-hidden transition-all duration-300 origin-bottom-right">
            <!-- Header -->
            <div class="bg-primary p-4 flex items-center justify-between text-white">
                <div class="flex items-center gap-3">
                    <div class="relative">
                        <img src="chatbot-avatar.png" alt="Asesor" class="w-10 h-10 rounded-full object-cover border-2 border-white/20">
                        <span class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-primary rounded-full"></span>
                    </div>
                    <div>
                        <h3 class="font-bold text-sm">Asesor Experto</h3>
                        <p class="text-xs text-white/80">En línea</p>
                    </div>
                </div>
                <button id="close-chatbot" class="text-white/80 hover:text-white transition-colors">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <!-- Chat Body -->
            <div class="flex-1 p-4 bg-slate-50 dark:bg-slate-800 overflow-y-auto">
                <div class="text-center text-xs text-slate-400 mb-4">Hoy</div>
                <div class="flex gap-3 mb-4">
                    <img src="chatbot-avatar.png" alt="Asesor" class="w-8 h-8 rounded-full object-cover mt-1">
                    <div class="bg-white dark:bg-slate-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700 dark:text-slate-200 border border-slate-100 dark:border-slate-600">
                        ¡Hola! Soy tu asesor experto en césped sintético. ¿En qué puedo ayudarte hoy para transformar tu espacio?
                    </div>
                </div>
            </div>
            <!-- Chat Input (Ready for n8n) -->
            <div class="p-3 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
                <form id="chat-form" class="flex items-center gap-2">
                    <input type="text" id="chat-input" placeholder="Escribe tu mensaje..." class="flex-1 bg-slate-100 dark:bg-slate-800 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 dark:text-white" required>
                    <button type="submit" class="bg-primary text-white p-2 rounded-full w-9 h-9 flex items-center justify-center hover:bg-primary/90 transition-colors">
                        <span class="material-symbols-outlined text-sm">send</span>
                    </button>
                </form>
            </div>
        </div>
        
        <!-- Chat Button -->
        <button id="chatbot-button" class="relative group flex items-center justify-center w-16 h-16 rounded-full bg-white dark:bg-slate-800 shadow-xl border-2 border-primary hover:scale-105 transition-transform duration-300">
            <img src="chatbot-avatar.png" alt="Abrir Chat" class="w-full h-full rounded-full object-cover">
            <span class="absolute -top-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white dark:border-slate-800 rounded-full"></span>
            <div class="absolute right-full mr-4 bg-black/80 text-white text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                ¿Necesitas ayuda?
            </div>
        </button>
    </div>

    <!-- Chatbot Logic -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chatbotButton = document.getElementById('chatbot-button');
            const chatbotWindow = document.getElementById('chatbot-window');
            const closeChatbot = document.getElementById('close-chatbot');
            const chatForm = document.getElementById('chat-form');
            const chatInput = document.getElementById('chat-input');
            const chatBody = chatbotWindow.querySelector('.overflow-y-auto');

            if(chatbotButton && chatbotWindow) {
                chatbotButton.addEventListener('click', () => {
                    chatbotWindow.classList.toggle('hidden');
                    if (!chatbotWindow.classList.contains('hidden')) {
                        chatInput.focus();
                    }
                });

                closeChatbot.addEventListener('click', () => {
                    chatbotWindow.classList.add('hidden');
                });

                chatForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const message = chatInput.value.trim();
                    if (message) {
                        // Add user message to UI
                        const userMsgHtml = `
                            <div class="flex gap-3 mb-4 justify-end">
                                <div class="bg-primary p-3 rounded-2xl rounded-tr-none shadow-sm text-sm text-white">
                                    ${message}
                                </div>
                            </div>
                        `;
                        chatBody.insertAdjacentHTML('beforeend', userMsgHtml);
                        chatInput.value = '';
                        chatBody.scrollTop = chatBody.scrollHeight;

                        // TODO: Connect to n8n webhook here
                        // fetch('URL_DE_TU_WEBHOOK_N8N', {
                        //     method: 'POST',
                        //     headers: { 'Content-Type': 'application/json' },
                        //     body: JSON.stringify({ message: message })
                        // });
                    }
                });
            }
        });
    </script>
</body>"""

for file_path in glob.glob("*.html"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if chatbot widget is already injected to avoid duplicates
    if 'id="chatbot-widget"' in content:
        print(f"Skipping {file_path}, chatbot already injected.")
        continue

    # Replace </body> with snippet
    if "</body>" in content:
        content = content.replace("</body>", html_snippet)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Injected into {file_path}")
    else:
        print(f"Warning: </body> not found in {file_path}")

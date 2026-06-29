// Sanitiza texto del usuario/LLM antes de insertarlo como HTML
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

document.addEventListener('DOMContentLoaded', () => {
    const chatbotButton = document.getElementById('chatbot-button');
    const chatbotWindow = document.getElementById('chatbot-window');
    const closeChatbot = document.getElementById('close-chatbot');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBody = chatbotWindow ? chatbotWindow.querySelector('.overflow-y-auto') : null;

    if (!chatbotButton || !chatbotWindow || !chatBody) return;

    // Generar o recuperar sessionId para el estado del chat
    let sessionId = sessionStorage.getItem('chatSessionId');
    if (!sessionId) {
        // If no session ID exists, check localStorage as fallback or create new
        sessionId = localStorage.getItem('chatSessionId') || "sess_" + crypto.randomUUID();
        sessionStorage.setItem('chatSessionId', sessionId);
        localStorage.setItem('chatSessionId', sessionId);
    }

    // Restore Chat State from sessionStorage
    const isChatOpen = sessionStorage.getItem('chatIsOpen') === 'true';
    if (isChatOpen) {
        chatbotWindow.classList.remove('hidden');
    }

    // Restore Chat History (append only — don't overwrite static welcome)
    const savedChatHistory = sessionStorage.getItem('chatHistory');
    if (savedChatHistory) {
        chatBody.insertAdjacentHTML('beforeend', savedChatHistory);
    }

    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;

    function saveChatState() {
        sessionStorage.setItem('chatIsOpen', !chatbotWindow.classList.contains('hidden'));
    }

    function saveChatHistory() {
        // Exclude static elements (welcome, today label) from saved history
        const dynamic = Array.from(chatBody.children)
            .filter(el => !el.dataset.static)
            .map(el => el.outerHTML)
            .join('');
        sessionStorage.setItem('chatHistory', dynamic);
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

    // Envía un mensaje programáticamente (usado por botones quick-reply)
    window.sendQuickMessage = function(msg) {
        if (chatInput.disabled) return;
        chatInput.value = msg;
        chatForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        chatInput.disabled = true;
        addMessage(escapeHtml(message), true);
        chatInput.value = '';
        const loaderId = addLoader();

        // Recuperar historial de mensajes guardado (máx 20 entradas)
        let chatHistory = [];
        try {
            const saved = sessionStorage.getItem('chatHistoryData');
            if (saved) chatHistory = JSON.parse(saved).slice(-20);
        } catch (e) { chatHistory = []; }

        try {
            // AI Agent v2 — Claude + Memory + Tools
            const response = await fetch(WEBHOOK_URL
                , {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        sessionId: sessionId
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

            // Detectar tag [CALCULAR] y añadir botón
            let calcularBtn = '';
            if (botReply.includes('[CALCULAR]')) {
                botReply = botReply.replace('[CALCULAR]', '').trim();
                calcularBtn = `<br><a href="calculadora.html" target="_blank" style="display:inline-block;margin-top:8px;padding:6px 14px;background:#16a34a;color:#fff;font-size:12px;font-weight:600;border-radius:12px;text-decoration:none;">📐 Calcular medidas</a>`;
            }

            // Detectar [PAYMENT_URL:...] y mostrar botón de Mercado Pago
            let pagoBtn = '';
            const paymentMatch = botReply.match(/\[PAYMENT_URL:(https?:\/\/[^\]]+)\]/);
            if (paymentMatch) {
                const paymentUrl = paymentMatch[1].trim();
                if (paymentUrl.startsWith('https://') && (paymentUrl.includes('mercadopago') || paymentUrl.includes('mercadolibre'))) {
                    botReply = botReply.replace(paymentMatch[0], '').trim();
                    pagoBtn = `<br><a href="${paymentUrl}" target="_blank" rel="noopener noreferrer" style="display:inline-block;margin-top:10px;padding:10px 22px;background:#009ee3;color:#fff;font-size:13px;font-weight:700;border-radius:14px;text-decoration:none;box-shadow:0 2px 8px rgba(0,158,227,0.35);">💳 Pagar con Mercado Pago</a>`;
                }
            }

            // Botón quick-reply PAGAR (aparece cuando el bot invita a iniciar el pago)
            let pagarQuickBtn = '';
            if (/escribe\s+pagar/i.test(botReply) && !paymentMatch) {
                pagarQuickBtn = `<br><button onclick="window.sendQuickMessage('PAGAR')" style="margin-top:8px;padding:8px 20px;background:#16a34a;color:#fff;font-size:12px;font-weight:700;border:none;border-radius:12px;cursor:pointer;">💳 PAGAR</button>`;
            }

            // Detectar [WZP:+XXXXXXXXX] y mostrar botón de WhatsApp
            let wzpBtn = '';
            const wzpMatch = botReply.match(/\[WZP:(\+\d+)\]/);
            if (wzpMatch) {
                const phone = wzpMatch[1];
                botReply = botReply.replace(wzpMatch[0], '').trim();
                wzpBtn = `<br><a href="https://wa.me/${phone.replace('+','')}" target="_blank" rel="noopener noreferrer" style="display:inline-block;margin-top:10px;padding:10px 22px;background:#25d366;color:#fff;font-size:13px;font-weight:700;border-radius:14px;text-decoration:none;box-shadow:0 2px 8px rgba(37,211,102,0.35);">💬 Hablar con un asesor</a>`;
            }

            addMessage(escapeHtml(botReply) + calcularBtn + pagoBtn + pagarQuickBtn + wzpBtn, false);

            // Guardar historial estructurado para enviar a n8n en el próximo mensaje
            try {
                const saved = sessionStorage.getItem('chatHistoryData');
                const hist = saved ? JSON.parse(saved) : [];
                hist.push({ role: 'user', content: message });
                hist.push({ role: 'assistant', content: botReply });
                sessionStorage.setItem('chatHistoryData', JSON.stringify(hist.slice(-40)));
            } catch (e) { /* ignorar */ }

        } catch (error) {
            console.error("Error connecting to n8n:", error);
            const loaderEl = document.getElementById(loaderId);
            if (loaderEl) {
                loaderEl.remove();
                saveChatHistory();
            }
            addMessage("No pude conectar con el servidor.", false);
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
        }
    });
});

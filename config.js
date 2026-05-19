// =====================================================
// CONFIGURACIÓN DE PRODUCCIÓN — Trato Hecho
// =====================================================
// Cambia WEBHOOK_URL por la URL pública de tu n8n
// Opciones:
//   - Local:   http://localhost:5678/webhook/chat-v2
//   - ngrok:   https://xxxx.ngrok-free.app/webhook/chat-v2
//   - Railway: https://tu-n8n.railway.app/webhook/chat-v2
// =====================================================

// URL LOCAL — Descomentar para desarrollo local con n8n corriendo en localhost
// const WEBHOOK_URL = 'http://localhost:5678/webhook/chat-v2';

// URL PRODUCCIÓN — Railway (activa)
const WEBHOOK_URL = 'https://main-production-38ed.up.railway.app/webhook/chat-v2';

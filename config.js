// =====================================================
// CONFIGURACIÃ“N DE PRODUCCIÃ“N â€” Trato Hecho
// =====================================================
// Cambia WEBHOOK_URL por la URL pÃºblica de tu n8n
// Opciones:
//   - Local:   http://localhost:5678/webhook/chat-v2
//   - ngrok:   https://xxxx.ngrok-free.app/webhook/chat-v2
//   - Railway: https://tu-n8n.railway.app/webhook/chat-v2
// =====================================================

// URL LOCAL â€” Descomentar para desarrollo local con n8n corriendo en localhost
// const WEBHOOK_URL = 'http://localhost:5678/webhook/chat-v2';

// URL EC2 (AWS Academy) â€” activa
const WEBHOOK_URL = 'http://34.195.161.246:5678/webhook/chat-v2';

// URL PRODUCCIÃ“N â€” Railway
// const WEBHOOK_URL = 'https://main-production-38ed.up.railway.app/webhook/chat-v2';

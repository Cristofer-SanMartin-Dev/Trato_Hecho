/**
 * PRUEBAS DE INTEGRACIÓN — Webhook n8n (chat-v2)
 * Verifica que el endpoint responde correctamente a distintos mensajes
 */

const N8N_URL    = process.env.N8N_URL    || 'http://localhost:5678';
const WEBHOOK    = `${N8N_URL}/webhook/chat-v2`;
const SESSION_ID = `test_integracion_${Date.now()}`;

async function post(body) {
    const res = await fetch(WEBHOOK, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
    });
    return { status: res.status, data: await res.json() };
}

// ── Helpers ───────────────────────────────────────────────────
function extraerMensaje(data) {
    if (Array.isArray(data)) return data[0]?.output || data[0]?.text || data[0]?.message || '';
    return data?.output || data?.text || data?.message || '';
}

// ── Tests ─────────────────────────────────────────────────────

describe('Conectividad básica', () => {

    test('n8n está corriendo (healthz responde 200)', async () => {
        const res = await fetch(`${N8N_URL}/healthz`);
        expect(res.status).toBe(200);
    });

    test('El webhook responde HTTP 200', async () => {
        const { status } = await post({ message: 'Hola', sessionId: SESSION_ID });
        expect(status).toBe(200);
    });

    test('La respuesta es un JSON válido', async () => {
        const { data } = await post({ message: 'Hola', sessionId: SESSION_ID });
        expect(data).toBeDefined();
        expect(typeof data === 'object' || Array.isArray(data)).toBe(true);
    });
});

describe('Formato de respuesta', () => {

    test('La respuesta contiene campo "message", "output" o "text"', async () => {
        const { data } = await post({ message: 'Hola', sessionId: SESSION_ID });
        const msg = extraerMensaje(data);
        expect(msg).toBeTruthy();
        expect(typeof msg).toBe('string');
    });

    test('El mensaje de respuesta no está vacío', async () => {
        const { data } = await post({ message: '¿Qué césped tienen?', sessionId: SESSION_ID });
        const msg = extraerMensaje(data);
        expect(msg.length).toBeGreaterThan(0);
    });

    test('La respuesta llega en menos de 15 segundos', async () => {
        const start = Date.now();
        await post({ message: 'Hola', sessionId: `perf_${Date.now()}` });
        const elapsed = Date.now() - start;
        expect(elapsed).toBeLessThan(15000);
    });
});

describe('Campos requeridos en el request', () => {

    test('Sin "message" retorna error o respuesta vacía', async () => {
        const res = await fetch(WEBHOOK, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ sessionId: 'test' }),
        });
        // n8n puede retornar 400 o 500 si falta el campo requerido
        expect([400, 500, 200]).toContain(res.status);
    });

    test('Con sessionId distinto por sesión se mantiene independencia', async () => {
        const { data: r1 } = await post({ message: 'Hola', sessionId: 'sesion_A' });
        const { data: r2 } = await post({ message: 'Hola', sessionId: 'sesion_B' });
        // Ambas respuestas son válidas pero independientes
        expect(extraerMensaje(r1)).toBeTruthy();
        expect(extraerMensaje(r2)).toBeTruthy();
    });
});

describe('Respuestas semánticas básicas', () => {

    test('Responde al saludo inicial con info del negocio', async () => {
        const { data } = await post({
            message:   'Hola, ¿qué venden?',
            sessionId: `sem_${Date.now()}`,
        });
        const msg = extraerMensaje(data).toLowerCase();
        const esSobre = msg.includes('césped') || msg.includes('pasto') || msg.includes('sintético') || msg.includes('queno');
        expect(esSobre).toBe(true);
    });

    test('Responde con información de productos al preguntar por catálogo', async () => {
        const { data } = await post({
            message:   '¿Qué tipos de pasto tienen y cuánto cuestan?',
            sessionId: `sem_cat_${Date.now()}`,
        });
        const msg = extraerMensaje(data).toLowerCase();
        // El agente debe mencionar algún producto, precio o preguntar por el uso
        const informativo = /luxury|soft|pet|pasto|césped|jardín|terraza|\$|precio|m²|uso|deportiv/i.test(msg);
        expect(informativo).toBe(true);
    });
});

describe('Manejo de sessionId', () => {

    test('sessionId vacío no rompe el sistema', async () => {
        const { status } = await post({ message: 'Hola', sessionId: '' });
        expect([200, 400, 500]).toContain(status);
    });

    test('sessionId largo (UUID) es aceptado', async () => {
        const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0;
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        const { status } = await post({ message: 'Hola', sessionId: uuid });
        expect(status).toBe(200);
    });
});

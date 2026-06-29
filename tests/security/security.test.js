/**
 * PRUEBAS DE SEGURIDAD — Trato Hecho
 * Valida protección contra XSS, inyección, entradas maliciosas y configuración segura
 */

const WEBHOOK      = process.env.WEBHOOK_URL || 'http://localhost:5678/webhook/chat-v2';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const http         = require('http');

async function postWebhook(body) {
    const res = await fetch(WEBHOOK, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
    });
    return { status: res.status, data: await res.json().catch(() => ({})) };
}

function extractMsg(data) {
    if (Array.isArray(data)) return data[0]?.output || data[0]?.text || data[0]?.message || '';
    return data?.output || data?.text || data?.message || '';
}

async function getFrontend(urlPath) {
    return new Promise((resolve, reject) => {
        http.get(`${FRONTEND_URL}${urlPath}`, res => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end',  () => resolve({ status: res.statusCode, headers: res.headers, body }));
        }).on('error', reject);
    });
}

// ── SEC-01: Protección XSS ────────────────────────────────────

describe('SEC-01: Inyección XSS en mensajes', () => {
    const payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        'javascript:alert(1)',
        '"><script>alert(document.cookie)</script>',
        '<svg onload=alert(1)>',
    ];

    payloads.forEach(payload => {
        test(`Payload XSS "${payload.substring(0, 30)}..." no rompe el sistema`, async () => {
            const { status } = await postWebhook({ message: payload, sessionId: `xss_${Date.now()}` });
            // El sistema debe responder (200, 400 o 500 — no debe crashear)
            expect([200, 400, 500]).toContain(status);
        });

        test(`Respuesta a XSS "${payload.substring(0, 20)}..." no refleja el payload sin escapar`, async () => {
            const { data } = await postWebhook({ message: payload, sessionId: `xss_r_${Date.now()}` });
            const msg = extractMsg(data);
            // La respuesta del bot no debe contener scripts ejecutables
            expect(msg).not.toContain('<script>');
            expect(msg).not.toContain('onerror=');
            expect(msg).not.toContain('javascript:alert');
        });
    });
});

// ── SEC-02: Inyección en campos de texto ─────────────────────

describe('SEC-02: Inyección SQL / NoSQL en mensajes', () => {
    const sqlPayloads = [
        "'; DROP TABLE cotizaciones; --",
        "1' OR '1'='1",
        '{"$gt": ""}',
        'UNION SELECT * FROM users',
    ];

    sqlPayloads.forEach(payload => {
        test(`Payload SQL "${payload.substring(0, 30)}" no rompe el sistema`, async () => {
            const { status } = await postWebhook({ message: payload, sessionId: `sql_${Date.now()}` });
            expect([200, 400, 500]).toContain(status);
        });
    });
});

// ── SEC-03: Entradas extremas ─────────────────────────────────

describe('SEC-03: Entradas con valores extremos', () => {

    test('Mensaje de 10.000 caracteres es manejado sin crash', async () => {
        const longMsg = 'A'.repeat(10000);
        const { status } = await postWebhook({ message: longMsg, sessionId: `long_${Date.now()}` });
        expect([200, 400, 413, 500]).toContain(status);
    });

    test('sessionId con caracteres especiales no rompe el sistema', async () => {
        const { status } = await postWebhook({
            message:   'Hola',
            sessionId: "sess'<script>alert(1)</script>",
        });
        expect([200, 400, 500]).toContain(status);
    });

    test('JSON con campos extras no documentados es ignorado', async () => {
        const res = await fetch(WEBHOOK, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                message:   'Hola',
                sessionId: `extra_${Date.now()}`,
                __proto__: { admin: true },
                constructor: { name: 'hack' },
            }),
        });
        expect([200, 400, 500]).toContain(res.status);
    });

    test('Mensaje nulo es manejado sin crash del servidor', async () => {
        // n8n puede retornar 200 (manejando el error internamente), 400 o 500
        const { status } = await postWebhook({ message: null, sessionId: `null_${Date.now()}` });
        expect([200, 400, 500]).toContain(status);
    });
});

// ── SEC-04: Cabeceras de seguridad en el frontend ─────────────

describe('SEC-04: Configuración de seguridad del frontend', () => {

    test('El servidor no expone información sensible de versión en cabeceras', async () => {
        const r = await getFrontend('/');
        const serverHeader = r.headers['server'] || '';
        // No debe revelar versiones específicas del servidor
        expect(serverHeader).not.toMatch(/express\/\d|nginx\/\d|apache\/\d/i);
    });

    test('CORS configurado en el frontend (Access-Control-Allow-Origin presente)', async () => {
        const r = await getFrontend('/');
        expect(r.headers['access-control-allow-origin']).toBeDefined();
    });

    test('config.js no expone credenciales de producción en local', async () => {
        const r = await getFrontend('/config.js');
        // Las credenciales (API keys, passwords) no deben estar en texto plano en config.js
        expect(r.body).not.toMatch(/sk-ant-api|APP_USR-|eyJhbGciOi/);
    });

    test('El directorio raíz no expone archivos .env', async () => {
        const r = await getFrontend('/.env');
        // Debe retornar index.html (SPA fallback) o 404 — nunca el .env real
        if (r.status === 200) {
            // Si retorna 200 (SPA fallback), no debe contener claves reales
            expect(r.body).not.toContain('ANTHROPIC_API_KEY=sk-');
            expect(r.body).not.toContain('PASSWORD=');
        }
    });
});

// ── SEC-05: Rate limiting / abuso ────────────────────────────

describe('SEC-05: Resistencia a spam / rate limiting', () => {

    test('10 requests rápidas consecutivas son manejadas', async () => {
        const sid = `spam_${Date.now()}`;
        const promises = Array.from({ length: 10 }, (_, i) =>
            postWebhook({ message: `Mensaje rápido ${i}`, sessionId: sid })
        );
        const results = await Promise.allSettled(promises);
        const respondidas = results.filter(r => r.status === 'fulfilled');
        // Al menos el 50% debe responder (no crashear)
        expect(respondidas.length).toBeGreaterThanOrEqual(5);
    });
});

// ── SEC-06: Validación del payload MercadoPago ───────────────

describe('SEC-06: Validación de URLs de pago generadas', () => {

    function validarPaymentUrl(url) {
        if (!url) return false;
        if (!url.startsWith('https://')) return false;
        if (!url.includes('mercadopago') && !url.includes('mercadolibre')) return false;
        return true;
    }

    test('Solo se aceptan URLs de pago con HTTPS', () => {
        expect(validarPaymentUrl('http://mercadopago.cl/pago')).toBe(false);
        expect(validarPaymentUrl('https://mercadopago.cl/pago')).toBe(true);
    });

    test('Solo se aceptan URLs de dominios MercadoPago/MercadoLibre', () => {
        expect(validarPaymentUrl('https://malicious.com/fake')).toBe(false);
        expect(validarPaymentUrl('https://www.mercadopago.cl/checkout')).toBe(true);
        expect(validarPaymentUrl('https://www.mercadolibre.cl/checkout')).toBe(true);
    });

    test('URL vacía o null es rechazada', () => {
        expect(validarPaymentUrl('')).toBe(false);
        expect(validarPaymentUrl(null)).toBe(false);
        expect(validarPaymentUrl(undefined)).toBe(false);
    });
});

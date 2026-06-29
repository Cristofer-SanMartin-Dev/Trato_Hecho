/**
 * PRUEBAS DE INTEGRACIÓN — Servidor de frontend
 * Verifica que server.js sirve correctamente los archivos estáticos
 */

const http = require('http');
const path = require('path');
const fs   = require('fs');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

async function get(urlPath) {
    return new Promise((resolve, reject) => {
        const url = new URL(urlPath, FRONTEND_URL);
        http.get(url.toString(), (res) => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end',  () => resolve({ status: res.statusCode, headers: res.headers, body }));
        }).on('error', reject);
    });
}

describe('Servidor frontend (puerto 3000)', () => {

    test('Responde en el puerto 3000', async () => {
        const r = await get('/');
        expect(r.status).toBe(200);
    });

    test('Sirve index.html en la raíz', async () => {
        const r = await get('/');
        expect(r.body).toContain('<!DOCTYPE html');
    });

    test('Sirve chatbot.js con Content-Type JavaScript', async () => {
        const r = await get('/chatbot.js');
        expect(r.status).toBe(200);
        expect(r.headers['content-type']).toContain('javascript');
    });

    test('Sirve config.js', async () => {
        const r = await get('/config.js');
        expect(r.status).toBe(200);
        expect(r.body).toContain('WEBHOOK_URL');
    });

    test('Sirve calculadora.html', async () => {
        const r = await get('/calculadora.html');
        expect(r.status).toBe(200);
        expect(r.body).toContain('<!DOCTYPE html');
    });

    test('Sirve contacto.html', async () => {
        const r = await get('/contacto.html');
        expect(r.status).toBe(200);
    });

    test('Sirve jardines.html', async () => {
        const r = await get('/jardines.html');
        expect(r.status).toBe(200);
    });

    test('Sirve pasto-deportivo.html', async () => {
        const r = await get('/pasto-deportivo.html');
        expect(r.status).toBe(200);
    });

    test('Tiene cabecera CORS (Access-Control-Allow-Origin)', async () => {
        const r = await get('/');
        expect(r.headers['access-control-allow-origin']).toBe('*');
    });

    test('Ruta inexistente sirve index.html (SPA fallback)', async () => {
        const r = await get('/ruta-que-no-existe');
        expect(r.status).toBe(200);
        expect(r.body).toContain('<!DOCTYPE html');
    });

    test('index.html menciona "Césped" o "Pasto"', async () => {
        const r = await get('/');
        expect(r.body).toMatch(/[Cc]é?sped|[Pp]asto/i);
    });

    test('index.html contiene el código del chatbot (inline o externo)', async () => {
        const r = await get('/');
        // El chatbot puede estar inline (<script>) o como archivo externo
        const tieneChatbot = r.body.includes('chatbot.js') || r.body.includes('WEBHOOK_URL') || r.body.includes('chatbotButton') || r.body.includes('sendMessage');
        expect(tieneChatbot).toBe(true);
    });

    test('index.html carga config.js', async () => {
        const r = await get('/');
        expect(r.body).toContain('config.js');
    });
});

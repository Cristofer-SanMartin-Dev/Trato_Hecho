/**
 * PRUEBAS UNITARIAS — Configuración del sistema (config.js)
 */

const fs   = require('fs');
const path = require('path');

const CONFIG_PATH = path.resolve(__dirname, '../../config.js');

function leerWebhookUrl() {
    const content = fs.readFileSync(CONFIG_PATH, 'utf-8');
    // Buscar la línea activa (no comentada) con WEBHOOK_URL
    const match = content.match(/^(?!\/\/).*const WEBHOOK_URL\s*=\s*['"]([^'"]+)['"]/m);
    return match ? match[1] : null;
}

describe('config.js — configuración del webhook', () => {

    test('El archivo config.js existe', () => {
        expect(fs.existsSync(CONFIG_PATH)).toBe(true);
    });

    test('Tiene una WEBHOOK_URL activa (no comentada)', () => {
        const url = leerWebhookUrl();
        expect(url).not.toBeNull();
    });

    test('La WEBHOOK_URL activa es una URL válida', () => {
        const url = leerWebhookUrl();
        expect(url).toMatch(/^https?:\/\/.+/);
    });

    test('La WEBHOOK_URL apunta al endpoint /webhook/chat-v2', () => {
        const url = leerWebhookUrl();
        expect(url).toContain('/webhook/chat-v2');
    });

    test('No tiene dos WEBHOOK_URL activas simultáneamente', () => {
        const content = fs.readFileSync(CONFIG_PATH, 'utf-8');
        const activas = content
            .split('\n')
            .filter(l => l.match(/^(?!\/\/).*const WEBHOOK_URL\s*=/));
        expect(activas.length).toBeLessThanOrEqual(1);
    });
});

describe('server.js — servidor de desarrollo', () => {
    const SERVER_PATH = path.resolve(__dirname, '../../server.js');

    test('El archivo server.js existe', () => {
        expect(fs.existsSync(SERVER_PATH)).toBe(true);
    });

    test('Usa el puerto 3000 por defecto', () => {
        const content = fs.readFileSync(SERVER_PATH, 'utf-8');
        expect(content).toContain('3000');
    });

    test('Tiene cabecera CORS Access-Control-Allow-Origin', () => {
        const content = fs.readFileSync(SERVER_PATH, 'utf-8');
        expect(content).toContain('Access-Control-Allow-Origin');
    });
});

describe('Archivos HTML requeridos', () => {
    const htmlFiles = ['index.html', 'contacto.html', 'calculadora.html', 'jardines.html', 'insumos.html', 'pasto-deportivo.html'];
    const ROOT = path.resolve(__dirname, '../..');

    htmlFiles.forEach(file => {
        test(`${file} existe`, () => {
            expect(fs.existsSync(path.join(ROOT, file))).toBe(true);
        });
    });

    test('chatbot.js existe', () => {
        expect(fs.existsSync(path.join(ROOT, 'chatbot.js'))).toBe(true);
    });
});

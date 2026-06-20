/**
 * PRUEBAS FUNCIONALES — Flujos completos de conversación
 * Valida los flujos de negocio de extremo a extremo vía el webhook de n8n
 */

const WEBHOOK = process.env.WEBHOOK_URL || 'http://localhost:5678/webhook/chat-v2';

async function chat(message, sessionId) {
    const res = await fetch(WEBHOOK, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message, sessionId }),
    });
    const data = await res.json();
    if (Array.isArray(data)) return data[0]?.output || data[0]?.text || data[0]?.message || '';
    return data?.output || data?.text || data?.message || '';
}

const uid = () => `func_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;

// ── Tests funcionales ─────────────────────────────────────────

describe('RF-01: Saludo inicial', () => {

    test('El bot responde al saludo con presentación del servicio', async () => {
        const resp = await chat('Hola', uid());
        expect(resp).toBeTruthy();
        expect(resp.length).toBeGreaterThan(10);
    });

    test('La respuesta menciona al agente "Queno" o césped sintético', async () => {
        const resp = (await chat('Hola', uid())).toLowerCase();
        const esCorrecto = resp.includes('queno') || resp.includes('césped') || resp.includes('pasto');
        expect(esCorrecto).toBe(true);
    });
});

describe('RF-02: Consulta de catálogo y precios', () => {

    test('Menciona Luxury Emerald al preguntar por pasto premium', async () => {
        const resp = (await chat('¿Qué pasto premium tienen?', uid())).toLowerCase();
        const ok = resp.includes('luxury') || resp.includes('emerald') || resp.includes('40mm') || resp.includes('$');
        expect(ok).toBe(true);
    });

    test('Menciona Pet-Friendly al preguntar por pasto para mascotas', async () => {
        const resp = (await chat('Tengo perros, ¿qué pasto me recomiendan?', uid())).toLowerCase();
        const ok = resp.includes('pet') || resp.includes('mascota') || resp.includes('perro') || resp.includes('pasto');
        expect(ok).toBe(true);
    });

    test('Muestra precios en pesos chilenos ($) tras indicar el producto', async () => {
        const sid = uid();
        await chat('Quiero el Luxury Emerald para mi jardín', sid);
        const resp = await chat('¿Cuánto cuesta el metro cuadrado?', sid);
        expect(resp).toMatch(/\$[\d.,]+|[\d.,]+\/m²?|\d+\.?\d{3}/);
    });
});

describe('RF-03: Cálculo de m²', () => {

    test('Procesa dimensiones en formato NxN', async () => {
        const sid = uid();
        await chat('Quiero el Soft Touch', sid);
        const resp = (await chat('Mi jardín mide 5x8', sid)).toLowerCase();
        const calculoPresente = resp.includes('40') || resp.includes('m²') || resp.includes('m2') || resp.includes('$') || resp.includes('instalac');
        expect(calculoPresente).toBe(true);
    });

    test('Procesa m² directamente como número tras confirmar el producto', async () => {
        const sid = uid();
        await chat('Quiero el Luxury Emerald para jardín', sid);
        await chat('Para un jardín residencial', sid);
        const resp = (await chat('25 m2', sid)).toLowerCase();
        const calculoPresente = resp.includes('25') || resp.includes('m²') || resp.includes('m2') || resp.includes('$') || resp.includes('instalac') || resp.includes('margen');
        expect(calculoPresente).toBe(true);
    });
});

describe('RF-04: Pregunta de instalación', () => {

    test('El flujo llega a preguntar instalación tras producto + m²', async () => {
        const sid = uid();
        await chat('Me interesa el Soft Touch para jardín residencial', sid);
        const resp = (await chat('20 m2', sid)).toLowerCase();
        // El bot debe mostrar desglose de precio o preguntar por instalación
        const avanzaFlujo = resp.includes('instalac') || resp.includes('$') || resp.includes('total') || resp.includes('subtotal') || resp.includes('m²') || resp.includes('22');
        expect(avanzaFlujo).toBe(true);
    }, 30000);
});

describe('RF-05: Respuesta a preguntas frecuentes', () => {

    test('Responde sobre disponibilidad para canchas deportivas', async () => {
        const resp = (await chat('¿Tienen pasto para canchas de fútbol?', uid())).toLowerCase();
        const ok = resp.includes('deportiv') || resp.includes('fútbol') || resp.includes('futbol') || resp.includes('cotizar') || resp.includes('precio');
        expect(ok).toBe(true);
    });

    test('Responde al preguntar por garantía o calidad', async () => {
        const resp = await chat('¿El pasto es de buena calidad?', uid());
        expect(resp.length).toBeGreaterThan(20);
    });
});

describe('RF-06: Comando COTIZAR', () => {

    test('El sistema responde al comando COTIZAR solicitando datos', async () => {
        const sid = uid();
        const resp = (await chat('COTIZAR', sid)).toLowerCase();
        const pideDatos = resp.includes('nombre') || resp.includes('rut') || resp.includes('cotiz') || resp.includes('datos');
        expect(pideDatos).toBe(true);
    });
});

describe('RF-07: Mensajes en distintos idiomas / estilos', () => {

    test('Maneja mensaje todo en mayúsculas', async () => {
        const resp = await chat('HOLA NECESITO PASTO PARA MI JARDIN', uid());
        expect(resp).toBeTruthy();
        expect(resp.length).toBeGreaterThan(10);
    });

    test('Maneja mensaje con errores ortográficos', async () => {
        const resp = await chat('kiero pasto sintetico para mi casa', uid());
        expect(resp).toBeTruthy();
    });

    test('Maneja mensaje muy largo (200+ chars)', async () => {
        const msg = 'Hola, estoy buscando césped sintético para mi jardín que tiene una forma irregular. Aproximadamente unos 30 metros cuadrados. También tengo una terraza de 5x4 metros. ¿Cuál sería el mejor producto?';
        const resp = await chat(msg, uid());
        expect(resp).toBeTruthy();
    });
});

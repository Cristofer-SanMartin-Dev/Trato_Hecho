/**
 * PRUEBAS UNITARIAS — Lógica del chatbot (funciones puras extraídas de chatbot.js)
 */

// ── Funciones puras reproducidas del chatbot ──────────────────

function generarSessionId() {
    return 'sess_' + Math.random().toString(36).substr(2, 9);
}

function detectarTagCalcular(texto) {
    return texto.includes('[CALCULAR]');
}

function detectarPaymentUrl(texto) {
    const match = texto.match(/\[PAYMENT_URL:(https?:\/\/[^\]]+)\]/);
    if (!match) return null;
    const url = match[1].trim();
    if (url.startsWith('https://') && (url.includes('mercadopago') || url.includes('mercadolibre'))) {
        return url;
    }
    return null;
}

function detectarWhatsApp(texto) {
    const match = texto.match(/\[WZP:(\+\d+)\]/);
    return match ? match[1] : null;
}

function limpiarTextoRespuesta(texto) {
    return texto
        .replace(/\[CALCULAR\]/g, '')
        .replace(/\[PAYMENT_URL:[^\]]+\]/g, '')
        .replace(/\[WZP:\+\d+\]/g, '')
        .trim();
}

function extraerMensajeBot(data) {
    if (Array.isArray(data)) {
        return data[0]?.output || data[0]?.text || data[0]?.message || null;
    }
    return data?.output || data?.text || data?.message || null;
}

function validarMensaje(msg) {
    if (!msg || typeof msg !== 'string') return false;
    return msg.trim().length > 0;
}

// ── Tests ─────────────────────────────────────────────────────

describe('sessionId', () => {
    test('Tiene formato "sess_" + 9 chars alfanuméricos', () => {
        const id = generarSessionId();
        expect(id).toMatch(/^sess_[a-z0-9]{9}$/);
    });

    test('Dos IDs generados consecutivamente son distintos', () => {
        const id1 = generarSessionId();
        const id2 = generarSessionId();
        expect(id1).not.toBe(id2);
    });

    test('100 IDs generados son todos únicos', () => {
        const ids = new Set(Array.from({ length: 100 }, generarSessionId));
        expect(ids.size).toBe(100);
    });
});

describe('Detección de tag [CALCULAR]', () => {
    test('Detecta el tag en respuesta del bot', () => {
        const resp = 'Para medir tu jardín, usa una cinta métrica. [CALCULAR]';
        expect(detectarTagCalcular(resp)).toBe(true);
    });

    test('No detecta si no está presente', () => {
        expect(detectarTagCalcular('El precio es $500.000')).toBe(false);
    });

    test('Es case-sensitive (solo mayúsculas)', () => {
        expect(detectarTagCalcular('[calcular]')).toBe(false);
        expect(detectarTagCalcular('[Calcular]')).toBe(false);
    });
});

describe('Detección de [PAYMENT_URL:...]', () => {
    test('Detecta URL de MercadoPago válida', () => {
        const resp = 'Aquí tu link de pago: [PAYMENT_URL:https://www.mercadopago.cl/checkout/v1/redirect?pref_id=abc123]';
        const url = detectarPaymentUrl(resp);
        expect(url).toBeTruthy();
        expect(url).toContain('mercadopago.cl');
    });

    test('Detecta URL de MercadoLibre válida', () => {
        const resp = '[PAYMENT_URL:https://www.mercadolibre.cl/checkout/redirect?id=xyz]';
        expect(detectarPaymentUrl(resp)).toBeTruthy();
    });

    test('No detecta URL HTTP insegura', () => {
        const resp = '[PAYMENT_URL:http://mercadopago.cl/pago]';
        expect(detectarPaymentUrl(resp)).toBeNull();
    });

    test('No detecta URL de dominio no esperado', () => {
        const resp = '[PAYMENT_URL:https://malicious.com/fake]';
        expect(detectarPaymentUrl(resp)).toBeNull();
    });

    test('Retorna null si no hay tag', () => {
        expect(detectarPaymentUrl('Tu cotización está lista.')).toBeNull();
    });
});

describe('Detección de [WZP:+número]', () => {
    test('Detecta número chileno con código país', () => {
        const resp = 'Contáctanos aquí [WZP:+56912345678]';
        expect(detectarWhatsApp(resp)).toBe('+56912345678');
    });

    test('Retorna null si no hay tag', () => {
        expect(detectarWhatsApp('Escríbenos por WhatsApp')).toBeNull();
    });
});

describe('Limpieza de texto de respuesta', () => {
    test('Elimina [CALCULAR] del texto', () => {
        const limpio = limpiarTextoRespuesta('Mide tu jardín. [CALCULAR]');
        expect(limpio).not.toContain('[CALCULAR]');
    });

    test('Elimina [PAYMENT_URL:...] del texto', () => {
        const limpio = limpiarTextoRespuesta('Paga aquí [PAYMENT_URL:https://mercadopago.cl/abc]');
        expect(limpio).not.toContain('[PAYMENT_URL:');
    });

    test('Elimina [WZP:...] del texto', () => {
        const limpio = limpiarTextoRespuesta('Contáctanos [WZP:+56912345678]');
        expect(limpio).not.toContain('[WZP:');
    });

    test('No modifica texto sin tags', () => {
        const texto = 'El precio del césped es $280.000.';
        expect(limpiarTextoRespuesta(texto)).toBe(texto);
    });
});

describe('Extracción de mensaje del bot desde respuesta n8n', () => {
    test('Array con .output', () => {
        expect(extraerMensajeBot([{ output: 'Hola!' }])).toBe('Hola!');
    });

    test('Array con .text', () => {
        expect(extraerMensajeBot([{ text: 'Hola!' }])).toBe('Hola!');
    });

    test('Objeto con .message', () => {
        expect(extraerMensajeBot({ message: 'Hola!', action: 'CHAT' })).toBe('Hola!');
    });

    test('Objeto con .output', () => {
        expect(extraerMensajeBot({ output: 'Hola!', quote: null })).toBe('Hola!');
    });

    test('Array vacío retorna null', () => {
        expect(extraerMensajeBot([])).toBeNull();
    });

    test('null retorna null', () => {
        expect(extraerMensajeBot(null)).toBeNull();
    });
});

describe('Validación de mensaje del usuario', () => {
    test('Mensaje válido retorna true', () => {
        expect(validarMensaje('Quiero césped para mi jardín')).toBe(true);
    });

    test('String vacío retorna false', () => {
        expect(validarMensaje('')).toBe(false);
    });

    test('String solo espacios retorna false', () => {
        expect(validarMensaje('   ')).toBe(false);
    });

    test('null retorna false', () => {
        expect(validarMensaje(null)).toBe(false);
    });

    test('undefined retorna false', () => {
        expect(validarMensaje(undefined)).toBe(false);
    });

    test('Número retorna false', () => {
        expect(validarMensaje(123)).toBe(false);
    });
});

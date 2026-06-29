/**
 * PRUEBAS UNITARIAS — Lógica de cálculo de precios
 * Extrae y valida la misma lógica usada en el nodo "Construir Prompt Claude" del workflow n8n
 */

// ── Lógica extraída del workflow ──────────────────────────────
const CATALOGO = {
    'Luxury Emerald (40mm)':    { precio: 28500 },
    'Soft Touch (30mm)':        { precio: 22900 },
    'Pet-Friendly Turf (35mm)': { precio: 26000 },
};
const PRECIO_INSTALACION = 4500;

function calcularPrecio({ m2, producto, instalacion }) {
    if (!m2 || m2 <= 0) throw new Error('m2 debe ser mayor a 0');
    if (!CATALOGO[producto])  throw new Error(`Producto "${producto}" no existe en catálogo`);

    const precioPorM2  = CATALOGO[producto].precio;
    const m2Margen     = Math.ceil(m2 * 1.10);
    const subtotalPasto = m2Margen * precioPorM2;
    const subtotalInst  = instalacion ? m2Margen * PRECIO_INSTALACION : 0;
    const total         = subtotalPasto + subtotalInst;

    return { m2Margen, subtotalPasto, subtotalInst, total };
}

function parsearDimensiones(texto) {
    const matchDim = texto.match(/(\d+(?:[.,]\d+)?)\s*(?:x|×|por|\*)\s*(\d+(?:[.,]\d+)?)/i);
    if (matchDim) {
        const a = parseFloat(matchDim[1].replace(',', '.'));
        const b = parseFloat(matchDim[2].replace(',', '.'));
        return a * b;
    }
    const matchM2 = texto.trim().match(/^(\d+(?:[.,]\d+)?)\s*(?:m2|m²|mt2|mt|mts|metros?)?$/i);
    if (matchM2) return parseFloat(matchM2[1].replace(',', '.'));
    return null;
}

// ── Tests unitarios ───────────────────────────────────────────

describe('Cálculo de precios', () => {

    describe('Margen técnico (m2 × 1.10 redondeado hacia arriba)', () => {
        test('10 m² → margen 11 m²', () => {
            const r = calcularPrecio({ m2: 10, producto: 'Soft Touch (30mm)', instalacion: false });
            expect(r.m2Margen).toBe(11);
        });

        test('20 m² → margen 22 m²', () => {
            const r = calcularPrecio({ m2: 20, producto: 'Soft Touch (30mm)', instalacion: false });
            expect(r.m2Margen).toBe(22);
        });

        test('7.5 m² → margen 9 m² (ceil de 8.25)', () => {
            const r = calcularPrecio({ m2: 7.5, producto: 'Soft Touch (30mm)', instalacion: false });
            expect(r.m2Margen).toBe(Math.ceil(7.5 * 1.10)); // 9
        });

        test('Superficie exacta sin fracción conserva el ceil', () => {
            const r = calcularPrecio({ m2: 5, producto: 'Soft Touch (30mm)', instalacion: false });
            expect(r.m2Margen).toBe(6); // ceil(5 * 1.1) = ceil(5.5) = 6
        });
    });

    describe('Subtotal pasto por producto', () => {
        test('Luxury Emerald 10 m² → 11 m² × $28.500 = $313.500', () => {
            const r = calcularPrecio({ m2: 10, producto: 'Luxury Emerald (40mm)', instalacion: false });
            expect(r.subtotalPasto).toBe(11 * 28500); // 313500
        });

        test('Soft Touch 20 m² → 22 m² × $22.900 = $503.800', () => {
            const r = calcularPrecio({ m2: 20, producto: 'Soft Touch (30mm)', instalacion: false });
            expect(r.subtotalPasto).toBe(22 * 22900); // 503800
        });

        test('Pet-Friendly 15 m² → 17 m² × $26.000 = $442.000', () => {
            const r = calcularPrecio({ m2: 15, producto: 'Pet-Friendly Turf (35mm)', instalacion: false });
            expect(r.subtotalPasto).toBe(Math.ceil(15 * 1.1) * 26000);
        });
    });

    describe('Instalación opcional (+$4.500/m²)', () => {
        test('Con instalación: se suma al total', () => {
            const r = calcularPrecio({ m2: 10, producto: 'Soft Touch (30mm)', instalacion: true });
            expect(r.subtotalInst).toBe(r.m2Margen * 4500);
            expect(r.total).toBe(r.subtotalPasto + r.subtotalInst);
        });

        test('Sin instalación: subtotalInst es 0', () => {
            const r = calcularPrecio({ m2: 10, producto: 'Soft Touch (30mm)', instalacion: false });
            expect(r.subtotalInst).toBe(0);
            expect(r.total).toBe(r.subtotalPasto);
        });

        test('Total con instalación es mayor que sin instalación', () => {
            const sinInst  = calcularPrecio({ m2: 10, producto: 'Luxury Emerald (40mm)', instalacion: false });
            const conInst  = calcularPrecio({ m2: 10, producto: 'Luxury Emerald (40mm)', instalacion: true });
            expect(conInst.total).toBeGreaterThan(sinInst.total);
        });
    });

    describe('Validaciones de entrada', () => {
        test('m² <= 0 lanza error', () => {
            expect(() => calcularPrecio({ m2: 0, producto: 'Soft Touch (30mm)', instalacion: false }))
                .toThrow('m2 debe ser mayor a 0');
        });

        test('m² negativo lanza error', () => {
            expect(() => calcularPrecio({ m2: -5, producto: 'Soft Touch (30mm)', instalacion: false }))
                .toThrow();
        });

        test('Producto inexistente lanza error', () => {
            expect(() => calcularPrecio({ m2: 10, producto: 'Pasto Mágico', instalacion: false }))
                .toThrow('Producto "Pasto Mágico" no existe en catálogo');
        });
    });

    describe('Total final correcto (caso completo)', () => {
        test('Luxury 10 m² + instalación: $313.500 + $49.500 = $363.000', () => {
            const r = calcularPrecio({ m2: 10, producto: 'Luxury Emerald (40mm)', instalacion: true });
            // m2Margen = ceil(11) = 11
            // pasto    = 11 * 28500 = 313500
            // inst     = 11 * 4500  =  49500
            // total    = 363000
            expect(r.m2Margen).toBe(11);
            expect(r.subtotalPasto).toBe(313500);
            expect(r.subtotalInst).toBe(49500);
            expect(r.total).toBe(363000);
        });
    });
});

describe('Parseo de dimensiones', () => {
    test('"5x8" → 40 m²', ()    => expect(parsearDimensiones('5x8')).toBe(40));
    test('"5 por 8" → 40 m²', () => expect(parsearDimensiones('5 por 8')).toBe(40));
    test('"5×8" → 40 m²', ()    => expect(parsearDimensiones('5×8')).toBe(40));
    test('"5 * 8" → 40 m²', ()  => expect(parsearDimensiones('5 * 8')).toBe(40));
    test('"20" → 20 m²', ()     => expect(parsearDimensiones('20')).toBe(20));
    test('"20 m2" → 20 m²', ()  => expect(parsearDimensiones('20 m2')).toBe(20));
    test('"20 m²" → 20 m²', ()  => expect(parsearDimensiones('20 m²')).toBe(20));
    test('"20 metros" → 20 m²', () => expect(parsearDimensiones('20 metros')).toBe(20));
    test('"3,5x4" → 14 m²', ()  => expect(parsearDimensiones('3,5x4')).toBe(14));
    test('"hola amigo" → null', () => expect(parsearDimensiones('hola amigo')).toBeNull());
    test('"COTIZAR" → null', () => expect(parsearDimensiones('COTIZAR')).toBeNull());
});

describe('Catálogo de productos', () => {
    test('Tiene exactamente 3 productos residenciales', () => {
        expect(Object.keys(CATALOGO)).toHaveLength(3);
    });

    test('Luxury Emerald cuesta $28.500/m²', () => {
        expect(CATALOGO['Luxury Emerald (40mm)'].precio).toBe(28500);
    });

    test('Soft Touch cuesta $22.900/m²', () => {
        expect(CATALOGO['Soft Touch (30mm)'].precio).toBe(22900);
    });

    test('Pet-Friendly cuesta $26.000/m²', () => {
        expect(CATALOGO['Pet-Friendly Turf (35mm)'].precio).toBe(26000);
    });

    test('Precio instalación es $4.500/m²', () => {
        expect(PRECIO_INSTALACION).toBe(4500);
    });
});

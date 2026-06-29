/**
 * PRUEBAS DE RENDIMIENTO — Trato Hecho
 * Mide tiempos de respuesta y capacidad bajo carga del webhook n8n
 * Ejecutar: node tests/performance/loadTest.js
 */

const WEBHOOK = process.env.WEBHOOK_URL || 'http://localhost:5678/webhook/chat-v2';

const SCENARIOS = [
    { name: 'Calentamiento',   concurrency: 1,  requests: 3,  label: 'baseline'   },
    { name: 'Carga baja',      concurrency: 2,  requests: 6,  label: 'low'        },
    { name: 'Carga media',     concurrency: 5,  requests: 15, label: 'medium'     },
    { name: 'Carga alta',      concurrency: 10, requests: 20, label: 'high'       },
];

const MESSAGES = [
    'Hola, necesito información sobre césped',
    '¿Qué tipos de pasto tienen?',
    'Quiero pasto para un jardín de 20 m2',
    '¿Cuánto cuesta el metro cuadrado?',
    'Tengo mascotas, ¿qué me recomiendan?',
];

function getMsg() {
    return MESSAGES[Math.floor(Math.random() * MESSAGES.length)];
}

async function singleRequest(id) {
    const start = Date.now();
    try {
        const res = await fetch(WEBHOOK, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                message:   getMsg(),
                sessionId: `perf_${id}_${Date.now()}`,
            }),
        });
        const elapsed = Date.now() - start;
        const data = await res.json().catch(() => ({}));
        const ok = res.status === 200;
        return { ok, status: res.status, elapsed, hasResponse: !!(data?.message || data?.output || data?.text || (Array.isArray(data) && data[0])) };
    } catch (err) {
        return { ok: false, status: 0, elapsed: Date.now() - start, error: err.message };
    }
}

async function runConcurrent(concurrency, total, scenarioName) {
    const results = [];
    let sent = 0;
    let active = 0;

    process.stdout.write(`  Ejecutando ${total} requests (${concurrency} concurrentes)...`);

    return new Promise((resolve) => {
        function launch() {
            while (active < concurrency && sent < total) {
                active++;
                const id = sent++;
                singleRequest(id).then(r => {
                    results.push(r);
                    active--;
                    process.stdout.write('.');
                    if (results.length === total) {
                        process.stdout.write('\n');
                        resolve(results);
                    } else {
                        launch();
                    }
                });
            }
        }
        launch();
    });
}

function stats(results) {
    const ok      = results.filter(r => r.ok);
    const times   = ok.map(r => r.elapsed).sort((a, b) => a - b);
    const avg     = times.length ? Math.round(times.reduce((a, b) => a + b, 0) / times.length) : 0;
    const p50     = times[Math.floor(times.length * 0.50)] || 0;
    const p90     = times[Math.floor(times.length * 0.90)] || 0;
    const p99     = times[Math.floor(times.length * 0.99)] || 0;
    const max     = times[times.length - 1] || 0;
    const min     = times[0] || 0;
    const errRate = ((results.length - ok.length) / results.length * 100).toFixed(1);

    return { total: results.length, ok: ok.length, errRate, avg, min, p50, p90, p99, max };
}

function printStats(label, s, thresholds) {
    const pass   = (val, max) => val <= max ? '✓' : '✗';
    const color  = (val, max) => val <= max ? '\x1b[32m' : '\x1b[31m';
    const reset  = '\x1b[0m';

    console.log(`\n  📊 ${label}`);
    console.log(`  ─────────────────────────────────────`);
    console.log(`  Requests:     ${s.total} total, ${s.ok} exitosos`);
    console.log(`  Error rate:   ${color(parseFloat(s.errRate), thresholds.errRate)}${s.errRate}%${reset} (umbral: ≤${thresholds.errRate}%)`);
    console.log(`  Tiempo mín:   ${s.min}ms`);
    console.log(`  Tiempo avg:   ${color(s.avg, thresholds.avg)}${s.avg}ms${reset} (umbral: ≤${thresholds.avg}ms) ${pass(s.avg, thresholds.avg)}`);
    console.log(`  P50:          ${color(s.p50, thresholds.p50)}${s.p50}ms${reset} (umbral: ≤${thresholds.p50}ms) ${pass(s.p50, thresholds.p50)}`);
    console.log(`  P90:          ${color(s.p90, thresholds.p90)}${s.p90}ms${reset} (umbral: ≤${thresholds.p90}ms) ${pass(s.p90, thresholds.p90)}`);
    console.log(`  P99:          ${color(s.p99, thresholds.p99)}${s.p99}ms${reset} (umbral: ≤${thresholds.p99}ms) ${pass(s.p99, thresholds.p99)}`);
    console.log(`  Tiempo máx:   ${s.max}ms`);

    const passed = s.avg <= thresholds.avg && s.p90 <= thresholds.p90 && parseFloat(s.errRate) <= thresholds.errRate;
    return passed;
}

async function main() {
    console.log('\n\x1b[36m============================================');
    console.log(' PRUEBAS DE RENDIMIENTO — Trato Hecho');
    console.log(`============================================\x1b[0m`);
    console.log(`  Webhook: ${WEBHOOK}`);
    console.log(`  Fecha:   ${new Date().toLocaleString('es-CL')}\n`);

    const THRESHOLDS = {
        baseline: { avg: 8000,  p50: 6000,  p90: 10000, p99: 15000, errRate: 0  },
        low:      { avg: 8000,  p50: 6000,  p90: 12000, p99: 18000, errRate: 5  },
        medium:   { avg: 10000, p50: 8000,  p90: 15000, p99: 20000, errRate: 10 },
        high:     { avg: 12000, p50: 10000, p90: 18000, p99: 25000, errRate: 20 },
    };

    const report = [];

    for (const scenario of SCENARIOS) {
        console.log(`\n  🚀 Escenario: ${scenario.name}`);
        const results = await runConcurrent(scenario.concurrency, scenario.requests, scenario.name);
        const s       = stats(results);
        const passed  = printStats(scenario.name, s, THRESHOLDS[scenario.label]);
        report.push({ scenario: scenario.name, stats: s, passed });
    }

    // ── Resumen final ─────────────────────────────────────────
    console.log('\n\x1b[36m============================================');
    console.log(' RESUMEN DE RENDIMIENTO');
    console.log('============================================\x1b[0m');
    report.forEach(r => {
        const icon = r.passed ? '\x1b[32m✓ PASS\x1b[0m' : '\x1b[31m✗ FAIL\x1b[0m';
        console.log(`  ${icon}  ${r.scenario} — P90: ${r.stats.p90}ms | Errores: ${r.stats.errRate}%`);
    });

    const allPassed = report.every(r => r.passed);
    console.log(`\n  Resultado global: ${allPassed ? '\x1b[32mTODOS LOS UMBRALES CUMPLIDOS\x1b[0m' : '\x1b[33mALGUNOS UMBRALES SUPERADOS\x1b[0m'}`);
    console.log('');

    // Guardar resultado en JSON para evidencia
    const fs = require('fs');
    const outPath = __dirname + '/results_' + Date.now() + '.json';
    fs.writeFileSync(outPath, JSON.stringify({ timestamp: new Date().toISOString(), webhook: WEBHOOK, report }, null, 2));
    console.log(`  📁 Resultados guardados en: ${outPath}\n`);

    process.exit(allPassed ? 0 : 1);
}

main().catch(err => {
    console.error('\x1b[31mError fatal en pruebas de rendimiento:', err.message, '\x1b[0m');
    process.exit(1);
});

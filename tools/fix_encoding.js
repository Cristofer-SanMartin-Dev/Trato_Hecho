/**
 * fix_encoding.js — Recupera caracteres españoles corrompidos a U+FFFD (◆)
 * Los HTMLs tienen el carácter de reemplazo Unicode donde deberían estar tildes.
 */
const fs = require('fs');

const FILES = [
  'index.html',
  'calculadora.html',
  'contacto.html',
  'jardines.html',
  'pasto-deportivo.html',
  'insumos.html',
];

// Reemplazos exactos de cadenas — de más específico a más general
// Formato: [buscar, reemplazar]
const FIXES = [
  // ── Palabras completas / frases únicas ────────────────────────────────────
  ['Sint�tico',     'Sintético'],
  ['sint�tico',     'sintético'],
  ['sint�ticas',    'sintéticas'],
  ['sint�tico,',    'sintético,'],
  ['sint�tico.',    'sintético.'],
  ['sint�tico:',    'sintético:'],
  ['sint�tico?',    'sintético?'],
  ['Sint�ticas',    'Sintéticas'],
  ['c�sped',        'césped'],
  ['C�sped',        'Césped'],
  ['cansped',             'césped'],  // por si acaso

  // ── Fútbol ────────────────────────────────────────────────────────────────
  ['F�tbol',        'Fútbol'],
  ['f�tbol',        'fútbol'],

  // ── Menú ─────────────────────────────────────────────────────────────────
  ['men�">',        'menú">'],
  ['Men� M',        'Menú M'],
  ['Men��',   'Menú'],  // doble corrupción

  // ── Instalación / Cotización / -ción palabras ────────────────────────────
  ['instalaci�n',   'instalación'],
  ['Instalaci�n',   'Instalación'],
  ['cotizaci�n',    'cotización'],
  ['Cotizaci�n',    'Cotización'],
  ['certificaci�n', 'certificación'],
  ['Certificaci�n', 'Certificación'],
  ['disposici�n',   'disposición'],
  ['posici�n',      'posición'],
  ['presentaci�n',  'presentación'],
  ['importaci�n',   'importación'],
  ['exportaci�n',   'exportación'],
  ['instalaci�n',   'instalación'],
  ['generaci�n',    'generación'],
  ['soluci�n',      'solución'],
  ['aplicaci�n',    'aplicación'],
  ['mantenci�n',    'mantención'],
  ['uni�n',         'unión'],
  ['izaci�n',       'ización'],
  ['aci�n',         'ación'],

  // ── Número ───────────────────────────────────────────────────────────────
  ['n�mero',        'número'],
  ['N�mero',        'Número'],

  // ── Básico ───────────────────────────────────────────────────────────────
  ['B�sico',        'Básico'],
  ['b�sico',        'básico'],

  // ── Línea ────────────────────────────────────────────────────────────────
  ['L�nea',         'Línea'],
  ['l�nea',         'línea'],
  ['en l�nea',      'en línea'],

  // ── Estándar ─────────────────────────────────────────────────────────────
  ['Est�ndar',      'Estándar'],
  ['est�ndar',      'estándar'],

  // ── Pádel ────────────────────────────────────────────────────────────────
  ['P�del',         'Pádel'],
  ['p�del',         'pádel'],

  // ── Líderes ──────────────────────────────────────────────────────────────
  ['L�deres',       'Líderes'],

  // ── Garantía ─────────────────────────────────────────────────────────────
  ['Garant�a',      'Garantía'],
  ['garant�a',      'garantía'],
  ['arant�a',       'arantía'],

  // ── Tecnología ───────────────────────────────────────────────────────────
  ['tecnolog�a',    'tecnología'],
  ['Tecnolog�a',    'Tecnología'],
  ['nolog�a',       'nología'],

  // ── Guía ─────────────────────────────────────────────────────────────────
  ['Gu�a',          'Guía'],
  ['gu�a',          'guía'],

  // ── Técnico / Técnica ────────────────────────────────────────────────────
  ['T�cnico',       'Técnico'],
  ['t�cnico',       'técnico'],
  ['T�cnica',       'Técnica'],
  ['t�cnica',       'técnica'],

  // ── Sílice ───────────────────────────────────────────────────────────────
  ['S�lice',        'Sílice'],
  ['s�lice',        'sílice'],

  // ── Teléfono ─────────────────────────────────────────────────────────────
  ['Tel�fono',      'Teléfono'],
  ['tel�fono',      'teléfono'],

  // ── Través ───────────────────────────────────────────────────────────────
  ['trav�s',        'través'],

  // ── Contáctanos / Contácta ───────────────────────────────────────────────
  ['Cont�ctanos',   'Contáctanos'],
  ['cont�ctanos',   'contáctanos'],
  ['Cont�ctate',    'Contáctate'],
  ['cont�cta',      'contácta'],

  // ── Años ─────────────────────────────────────────────────────────────────
  ['a�os',          'años'],
  ['A�os',          'Años'],

  // ── Reseñas ──────────────────────────────────────────────────────────────
  ['rese�as',       'reseñas'],

  // ── Máximo / Máxima / Máx ────────────────────────────────────────────────
  ['m�ximo',        'máximo'],
  ['m�xima',        'máxima'],
  ['M�ximo',        'Máximo'],
  ['m�x.',          'máx.'],
  ['m�x.',          'máx.'],
  ['(m�x.',         '(máx.'],

  // ── Cuántos ──────────────────────────────────────────────────────────────
  ['cu�ntos',       'cuántos'],

  // ── Está ─────────────────────────────────────────────────────────────────
  ['est� paga',     'está paga'],
  ['est� vige',     'está vige'],
  [' est� ',        ' está '],
  ['est�.',         'está.'],

  // ── Válido / Válida ──────────────────────────────────────────────────────
  ['v�lido',        'válido'],
  ['v�lida',        'válida'],

  // ── Dígitos ──────────────────────────────────────────────────────────────
  ['d�gitos',       'dígitos'],

  // ── Útil ─────────────────────────────────────────────────────────────────
  ['�til',          'útil'],

  // ── Término ──────────────────────────────────────────────────────────────
  ['T�rmino',       'Término'],
  ['t�rmino',       'término'],
  ['T�rminos',      'Términos'],
  ['t�rminos',      'términos'],

  // ── m² (metro cuadrado) ──────────────────────────────────────────────────
  ['/m�<',          '/m²<'],
  ['/m�\n',         '/m²\n'],
  ['/m� ',          '/m² '],
  ['m�</spa',       'm²</spa'],
  ['m�</p',         'm²</p'],
  ['por m�',        'por m²'],
  ['$m�',           'el m²'],

  // ── Signos de puntuación especiales ──────────────────────────────────────
  ['�Hola',         '¡Hola'],
  ['�En qu',        '¿En qu'],
  ['�Esta',         '¿Esta'],
  ['�Tiene',        '¿Tiene'],
  ['� 2024',        '© 2024'],
  ['� pued',        '¡ pued'],

  // ── Resto genérico por patrón de sufijo ──────────────────────────────────
  // (estas van AL FINAL para no sobrescribir los anteriores)
  ['ci�n',          'ción'],   // -ción genérico
  ['�n ',           'ón '],    // terminaciones -ón
  ['�n<',           'ón<'],
  ['�n"',           'ón"'],
  ['�n.',           'ón.'],
  ['�n,',           'ón,'],
];

let totalFixed = 0;

FILES.forEach(file => {
  if (!fs.existsSync(file)) return;
  let content = fs.readFileSync(file, 'utf8');
  const original = content;

  FIXES.forEach(([from, to]) => {
    while (content.includes(from)) {
      content = content.split(from).join(to);
    }
  });

  // Contar reemplazos restantes
  const remaining = (content.match(/�/g) || []).length;
  const fixed = (original.match(/�/g) || []).length - remaining;
  totalFixed += fixed;

  if (content !== original) {
    fs.writeFileSync(file, content, 'utf8');
    console.log(`${file}: ${fixed} corregidos, ${remaining} pendientes`);
  }
});

console.log(`\nTotal corregidos: ${totalFixed}`);
console.log('Verificación restantes:');
FILES.forEach(f => {
  if (!fs.existsSync(f)) return;
  const txt = fs.readFileSync(f, 'utf8');
  const rem = (txt.match(/�/g) || []).length;
  if (rem > 0) {
    console.log(`  ${f}: ${rem} pendientes`);
    [...txt.matchAll(/(.{0,10})�(.{0,10})/g)].slice(0,5).forEach(m =>
      console.log(`    → «${m[1]}[◆]${m[2]}»`)
    );
  }
});

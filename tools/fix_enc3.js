const fs = require('fs');
const R = '�';  // U+FFFD — carácter de reemplazo Unicode (el que está en los archivos)
const FILES = ['index.html','calculadora.html','contacto.html','jardines.html','pasto-deportivo.html','insumos.html'];

const FIXES = [
  // ─── Palabras pendientes ────────────────────────────────────────────────────
  ['M'+R+'vil','Móvil'],      ['m'+R+'vil','móvil'],
  ['m'+R+'ltiples','múltiples'],
  ['v'+R+'ley','vóley'],
  ['b'+R+'squetbol','básquetbol'],
  ['Est'+R+'tica','Estética'], ['est'+R+'tica','estética'],
  ['F'+R+'cil','Fácil'],      ['f'+R+'cil','fácil'],
  ['r'+R+'pido','rápido'],    ['R'+R+'pido','Rápido'],
  ['R'+R+'pida','Rápida'],
  ['h'+R+'drico','hídrico'],
  ['asesor'+R+'a','asesoría'],['Asesor'+R+'a','Asesoría'],
  [R+'ltima','\xFAltima'],[R+'ltimas','últimas'],[R+'ltimo','último'],
  ['tr'+R+'fico','tráfico'],
  ['Latinoam'+R+'rica','Latinoamérica'],
  ['Compa'+R+R+'a','Compañía'],['compa'+R+R+'a','compañía'],
  ['de '+R+'xito','de éxito'],[R+'xito','éxito'],
  [R+'rea ','Área '],  [R+'reas ','Áreas '],
  [R+'rea<','Área<'], [R+'reas<','Áreas<'],
  [R+'rea\n','Área\n'],
  ['tu '+R+'rea','tu Área'],
  ['tr'+R+'nsito','tránsito'],['Tr'+R+'nsito','Tránsito'],
  ['a'+R+'adir','añadir'],['A'+R+'adir','Añadir'],['A'+R+'ADIR','AÑADIR'],
  ['GU'+R+'A ','GUÍA '],['GU'+R+'A\n','GUÍA\n'],
  ['Gu'+R+'a','Guía'],['gu'+R+'a','guía'],
  ['Env'+R+'anos','Envíanos'],
  ['conf'+R+'a','confía'],
  ['P'+R+'rez','Pérez'],
  ['electr'+R+'nico','electrónico'],['Electr'+R+'nico','Electrónico'],
  ['qu'+R+' pode','qué pode'],['qu'+R+'"','qué"'],['qu'+R+'?','qué?'],
  ['en qu'+R,'en qué'],
  ['vac'+R+'o','vacío'],
  ['M'+R+'nimo','Mínimo'],['m'+R+'nimo','mínimo'],
  ['m'+R+'nima','mínima'],
  ['num'+R+'ricos','numéricos'],
  ['ten'+R+'a error','tenía error'],
  ['env'+R+'o','envío'],
  ['bot'+R+'n','botón'],
  ['Aseg'+R+'rate','Asegúrate'],
  ['p'+R+'gina','página'],['P'+R+'gina','Página'],
  [' m'+R+'s ',' más '],['m'+R+'s<','más<'],['m'+R+'s\n','más\n'],
  ['M'+R+'s ','Más '],
  ['Ni'+R+'os','Niños'],['ni'+R+'os','niños'],
  ['Insp'+R+'rate','Inspírate'],
  ['dise'+R+'o','diseño'],
  ['dise'+R+'adas','diseñadas'],['dise'+R+'ados','diseñados'],
  ['Categor'+R+'as','Categorías'],['categor'+R+'as','categorías'],
  ['jard'+R+'n','jardín'],['Jard'+R+'n','Jardín'],
  ['contempor'+R+'neo','contemporáneo'],
  [R+'Quieres','¿Quieres'],
  [R+'ptimo','Óptimo'],
  ['el pa'+R+'s','el país'],['do pa'+R+'s','do país'],
  ['ecol'+R+'gico','ecológico'],
  ['Cat'+R+'logo','Catálogo'],
  ['Pol'+R+'ticas','Políticas'],
  ['ayudar'+R+' a','ayudará a'],
  ['nolog'+R+'a','nología'],
  ['Inspecci'+R+'n','Inspección'],
  // m² en HTML y JS
  [R+' m\xB2','— m\xB2'],   // — m² (em dash como placeholder)
  [R+' <span','— <span'],         // — <span (reset de calculadora)
  ['m'+R+'\n','m\xB2\n'],         // m² al final de línea
  ['m'+R+' ','m\xB2 '],           // m² seguido de espacio
  ['m'+R+'\'','m\xB2\''],         // m² en string JS
  ['m'+R+'`','m\xB2`'],
  ['m'+R+'.','m\xB2.'],
  ['m'+R+'<','m\xB2<'],
  ['/m'+R,'/m\xB2'],
  ['} m'+R,'} m\xB2'],
  // × para dimensiones (${largo}m × ${ancho}m)
  ['}m '+R+' ${','}\m \xD7 ${'],
  ['}m '+R+' $','m \xD7 $'],
  // Signos de puntuación
  [R+'Listo','¡Listo'],[R+'solo','¡solo'],
  [R+'Mensaje','¡Mensaje'],
  [R+'No est','¿No est'],[R+'No sab','¿No sab'],
  [R+'Necesita','¿Necesita'],
  [R+'Quieres','¿Quieres'],
  [R+'En qu','¿En qu'],
  ['N'+R+' COT','N° COT'],
  [R+'ltima l','última l'],
  // patrón genérico -ión al final
  [R+'n ','ón '],  [R+'n,','ón,'],  [R+'n.','ón.'],
  [R+'n"','ón"'],  [R+'n<','ón<'],  [R+'n\n','ón\n'],
  // Comentarios JS
  ['m'+R+'  //','m² //'],
  ['// '+R,'// '],  // strips from comments (safe approximation)
  ['append only '+R+' don','append only — don'],
  ['webhook '+R+' configu','webhook — configu'],
  // INSTALACIÓN en mayúsculas
  ['INSTALACI'+R+'N','INSTALACIÓN'],
  // m² en compute comments
  ['compute m'+R,'compute m²'],
  // 2×2 en specs
  ['2'+R+'2','2×2'],
];

let total = 0;
FILES.forEach(f => {
  if (!fs.existsSync(f)) return;
  let c = fs.readFileSync(f, 'utf8');
  const before = (c.match(new RegExp(R,'g')) || []).length;
  if (before === 0) { process.stdout.write(f+': ya OK\n'); return; }
  FIXES.forEach(([from,to]) => { while (c.includes(from)) c = c.split(from).join(to); });
  const after = (c.match(new RegExp(R,'g')) || []).length;
  total += before - after;
  fs.writeFileSync(f, c, 'utf8');
  process.stdout.write(f+': '+(before-after)+' corregidos, '+after+' pendientes\n');
  if (after > 0) {
    [...c.matchAll(new RegExp('(.{0,20})'+R+'(.{0,20})','g'))].slice(0,8).forEach(m =>
      process.stdout.write('  «'+m[1]+'[X]'+m[2]+'»\n'));
  }
});
process.stdout.write('\nTotal: '+total+'\n');

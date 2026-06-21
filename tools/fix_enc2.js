const fs = require('fs');
const R = '�';
const FILES = ['index.html','calculadora.html','contacto.html','jardines.html','pasto-deportivo.html','insumos.html'];

const FIXES = [
  ['M'+R+'vil','Móvil'],    ['m'+R+'vil','móvil'],
  ['m'+R+'ltiples','múltiples'],
  ['v'+R+'ley','vóley'],
  ['Est'+R+'tica','Estética'],  ['est'+R+'tica','estética'],
  ['F'+R+'cil','Fácil'],     ['f'+R+'cil','fácil'],
  ['r'+R+'pido','rápido'],   ['R'+R+'pido','Rápido'],
  ['h'+R+'drico','hídrico'],
  ['asesor'+R+'a','asesoría'],  ['Asesor'+R+'a','Asesoría'],
  [R+'ltima','última'],  [R+'ltimas','últimas'],  [R+'ltimo','último'],
  ['tr'+R+'fico','tráfico'],
  ['Latinoam'+R+'rica','Latinoamérica'],
  ['Compa'+R+R+'a','Compañía'],
  ['de '+R+'xito','de éxito'],  [R+'xito','éxito'],
  [R+'rea de','Área de'],  [R+'rea </','Área </'],
  [R+'reas Inf','Áreas Inf'],  [R+'rea Inf','Área Inf'],
  [R+'rea</','Área</'],  ['gura tu '+R+'rea','gura tu Área'],
  ['tu '+R+'rea','tu Área'],
  ['tr'+R+'nsito','tránsito'],  ['Tr'+R+'nsito','Tránsito'],
  ['a'+R+'adir','añadir'],  ['A'+R+'adir','Añadir'],  ['A'+R+'ADIR','AÑADIR'],
  ['GU'+R+'A ','GUÍA '],  ['Gu'+R+'a ','Guía '],  ['Gu'+R+'a\n','Guía\n'],
  ['Env'+R+'anos','Envíanos'],
  ['conf'+R+'a ','confía '],
  ['P'+R+'rez','Pérez'],
  ['electr'+R+'nico','electrónico'],  ['Electr'+R+'nico','Electrónico'],
  ['en qu'+R+' pode','en qué pode'],  ['en qu'+R+'\n','en qué\n'],
  ['="'+R+'En qu','="¿En qu'],  ['"'+R+'En qu','"¿En qu'],
  ['vac'+R+'o','vacío'],
  ['M'+R+'nimo','Mínimo'],
  ['num'+R+'ricos','numéricos'],
  ['ya ten'+R+'a error','ya tenía error'],
  ['el env'+R+'o','el envío'],  ['env'+R+'o ','envío '],
  ['bot'+R+'n','botón'],
  ['Aseg'+R+'rate','Asegúrate'],
  ['p'+R+'gina','página'],  ['P'+R+'gina','Página'],
  [' m'+R+'s ',' más '],  ['m'+R+'s</p','más</p'],  ['M'+R+'s ','Más '],
  ['Ni'+R+'os','Niños'],  ['ni'+R+'os','niños'],  ['Apto Ni','Apto Niños'],
  ['Insp'+R+'rate','Inspírate'],
  ['dise'+R+'o ','diseño '],  ['dise'+R+'o\n','diseño\n'],  ['dise'+R+'o"','diseño"'],
  ['dise'+R+'adas','diseñadas'],  ['dise'+R+'ados','diseñados'],
  ['Categor'+R+'as','Categorías'],
  ['jard'+R+'n','jardín'],  ['Jard'+R+'n','Jardín'],
  ['contempor'+R+'neo','contemporáneo'],
  [R+'Quieres',  '¿Quieres'],
  [R+'ptimo','Óptimo'],
  ['el pa'+R+'s','el país'],  ['do el pa'+R+'s','do el país'],
  ['ecol'+R+'gico','ecológico'],
  ['Cat'+R+'logo','Catálogo'],
  ['Pol'+R+'ticas','Políticas'],
  ['ayudar'+R+' a','ayudará a'],
  ['nolog'+R+'a ','nología '],  ['nolog'+R+'a,','nología,'],  ['nolog'+R+'a.','nología.'],
  // m² en código JS dentro del HTML
  ['m'+R+'"',"m²\""],
  ["m"+R+"'",'m²\''],
  ['m'+R+'`','m²`'],
  ['m'+R+'.','m².'],
  ['m'+R+' ','m² '],
  ['/m'+R,'/m²'],
  ['m'+R+'<','m²<'],
  // Puntuación especial
  [R+'Listo ','¡Listo '],
  [R+'Mensaje ','¡Mensaje '],
  [R+'No est','¿No est'],
  [R+'No sab','¿No sab'],
  ['nueva, '+R+'solo','nueva, ¡solo'],
  [R+'Necesita','¿Necesita'],
  ['N'+R+' COT','N° COT'],
  // código JS
  [R+'ltima l','última l'],
  ['s el env'+R,'s el envío'],
  ['de '+R+'xito','de éxito'],
  ['el pa'+R,'el país'],
  // Patrones genéricos que quedan
  ['asesor'+R,'asesoría'],
  [R+'s </','s </'],
];

let total = 0;
FILES.forEach(f => {
  if (!fs.existsSync(f)) return;
  let c = fs.readFileSync(f, 'utf8');
  const before = (c.match(new RegExp(R,'g')) || []).length;
  FIXES.forEach(([from,to]) => { while (c.includes(from)) c = c.split(from).join(to); });
  const after = (c.match(new RegExp(R,'g')) || []).length;
  total += before - after;
  fs.writeFileSync(f, c, 'utf8');
  process.stdout.write(f + ': ' + (before-after) + ' corregidos, ' + after + ' pendientes\n');
  if (after > 0) {
    [...c.matchAll(new RegExp('(.{0,20})'+R+'(.{0,20})','g'))].slice(0,6).forEach(m =>
      process.stdout.write('  -> «' + m[1] + '[X]' + m[2] + '»\n'));
  }
});
process.stdout.write('\nTotal corregidos esta pasada: ' + total + '\n');

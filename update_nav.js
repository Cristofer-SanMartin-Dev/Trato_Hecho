const fs = require('fs');
const glob = require('glob');

const oldNav = `                <nav class="hidden lg:flex items-center gap-8">
                    <a class="text-sm font-semibold hover:text-primary transition-colors" href="index.html">Inicio</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="pasto-deportivo.html">Pasto Deportivo</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="jardines.html">Jardines</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors" href="insumos.html">Insumos y
                        Materiales</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="contacto.html">Contacto</a>
                    <a class="bg-primary/10 text-primary px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary hover:text-white transition-colors"
                        href="calculadora.html">Calculadora</a>
                </nav>`;

const newNav = `                <nav class="hidden lg:flex items-center gap-8">
                    <a class="text-sm font-semibold hover:text-primary transition-colors" href="index.html">Inicio</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="pasto-deportivo.html">Pasto Deportivo</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="jardines.html">Jardines</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors" href="insumos.html">Insumos y
                        Materiales</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="documento.html">Buscar Documento</a>
                    <a class="text-sm font-semibold hover:text-primary transition-colors"
                        href="contacto.html">Contacto</a>
                    <a class="bg-primary/10 text-primary px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary hover:text-white transition-colors"
                        href="calculadora.html">Calculadora</a>
                </nav>`;

const oldNav2 = `                    <nav class="hidden lg:flex items-center gap-8">
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="index.html">Inicio</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="pasto-deportivo.html">Pasto Deportivo</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="jardines.html">Jardines</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="insumos.html">Insumos y Materiales</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="contacto.html">Contacto</a>
                        <a class="bg-primary/10 text-primary px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary hover:text-white transition-colors"
                            href="calculadora.html">Calculadora</a>
                    </nav>`;

const newNav2 = `                    <nav class="hidden lg:flex items-center gap-8">
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="index.html">Inicio</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="pasto-deportivo.html">Pasto Deportivo</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="jardines.html">Jardines</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="insumos.html">Insumos y Materiales</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="documento.html">Buscar Documento</a>
                        <a class="text-sm font-semibold hover:text-primary transition-colors"
                            href="contacto.html">Contacto</a>
                        <a class="bg-primary/10 text-primary px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary hover:text-white transition-colors"
                            href="calculadora.html">Calculadora</a>
                    </nav>`;

const files = ['index.html', 'pasto-deportivo.html', 'jardines.html', 'insumos.html', 'contacto.html', 'calculadora.html'];

files.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    let modified = false;

    if (content.includes(oldNav)) {
        content = content.replace(oldNav, newNav);
        modified = true;
    } else if (content.includes(oldNav2)) {
        content = content.replace(oldNav2, newNav2);
        modified = true;
    }
    
    // Also try to replace by parsing or regex for more flexibility
    if (!modified) {
        // generic replacement for this specific block:
        // match <nav ... to </nav> and if it doesn't contain Buscar Documento, insert it before Contacto
        let match = content.match(/<nav class="hidden lg:flex items-center gap-8">([\s\S]*?)<\/nav>/);
        if (match && !match[0].includes("Buscar Documento")) {
            let inner = match[1];
            let navStr = `<nav class="hidden lg:flex items-center gap-8">`;
            let endStr = `</nav>`;
            // Find Contacto link
            let contactoIndex = inner.indexOf('href="contacto.html"');
            if (contactoIndex > -1) {
                // Find start of previous anchor tag
                let anchorStart = inner.lastIndexOf('<a', contactoIndex);
                if (anchorStart > -1) {
                    let insertStr = `\n                        <a class="text-sm font-semibold hover:text-primary transition-colors" href="documento.html">Buscar Documento</a>`;
                    let newInner = inner.substring(0, anchorStart) + insertStr + inner.substring(anchorStart-1);
                    content = content.replace(match[0], navStr + newInner + endStr);
                    modified = true;
                }
            }
        }
    }

    if (modified) {
        fs.writeFileSync(file, content, 'utf8');
        console.log(`Updated ${file}`);
    } else {
        console.log(`No updates made in ${file}`);
    }
});

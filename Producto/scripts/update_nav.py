import os
import glob

files = glob.glob('*.html')

old_nav = """                <nav class="hidden lg:flex items-center gap-8">
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
                </nav>"""

new_nav = """                <nav class="hidden lg:flex items-center gap-8">
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
                </nav>"""


old_nav_2 = """                    <nav class="hidden lg:flex items-center gap-8">
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
                    </nav>"""

new_nav_2 = """                    <nav class="hidden lg:flex items-center gap-8">
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
                    </nav>"""


for f in files:
    if f == 'documento.html': continue

    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    
    if old_nav in content:
        content = content.replace(old_nav, new_nav)
        modified = True
    elif old_nav_2 in content:
        content = content.replace(old_nav_2, new_nav_2)
        modified = True
    
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated nav in {f}")
    else:
        print(f"Nav string not found in {f}")

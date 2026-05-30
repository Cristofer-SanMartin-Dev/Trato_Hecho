import glob
import re
import os

template = """        <!-- Hero Section -->
        <section class="relative rounded-xl overflow-hidden mb-12 min-h-[300px] flex items-end">
            <div class="absolute inset-0 bg-cover bg-center"
                data-alt="Synthetic Grass"
                style="background-image: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.2) 60%), url('{bg_url}');">
            </div>
            <div class="relative p-8 md:p-12 w-full">
{content}
            </div>
        </section>"""

def get_bg_url(html):
    match = re.search(r"url\(['\"]?(https?://[^'\")]+)['\"]?\)", html)
    if match:
        return match.group(1)
    return "https://lh3.googleusercontent.com/aida-public/AB6AXuCyvYjkhVnkhit5kjPRBh0ATEkF9T3JAlGxa-Kg_DlZeAPV4alHZJtdeqgEeK2bumqugIhRDtg4rqCAyqYfycpvmwCxw4S0VcOj3_3cKbamaljL1S2UuEpgF69l4V9dzYjdD763KcUSQy_mJBjhlzNVeURMS2-4wa71ENgAS-IRfdJB743cadgXLrPn9PzL8ebYVZMSOjpjFfeIvOUAfaFBjxW7CthLxWQJOEFGJ7__ovYWF75rcw9PVVLm9OVwqKT1cejYAdMpRsA"

files = ["index.html", "jardines.html", "insumos.html", "calculadora.html", "contacto.html"]

for f in files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Simple regex to find the hero section. Since they vary, we use different matchers.
    # index: <section class="relative px-6 md:px-10 py-8"> ... </section>
    # calculadora: <section class="mb-12 text-center md:text-left"> ... </section>
    
    hero_pattern = r"(<!-- Hero Section -->|<!-- Navigation -->\s*</header>\s*<section.*?>|<main[^>]*>\s*<!-- Hero Section -->\s*<section.*?>|<main[^>]*>\s*<section.*?>)"
    
    # To be safe, let's manually replace for each file based on its structure
    if f == "index.html":
        s = re.search(r'(<!-- Hero Section -->.*?)(<!-- Pasto)', content, re.DOTALL)
        if s:
            bg = get_bg_url(s.group(1))
            inner = """                <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Transforma tus <span class="text-primary bg-white/90 px-2 rounded-lg">espacios</span></h1>
                <p class="text-white/80 max-w-2xl text-lg mb-6">Calidad premium en pasto sintético para residencias, áreas deportivas y comerciales. Durabilidad extrema y estética natural garantizada.</p>
                <button class="bg-primary text-white px-6 py-3 rounded-lg font-bold hover:bg-primary/90 transition-all">Cotizar Proyecto</button>"""
            new_hero = template.format(bg_url=bg, content=inner)
            content = content.replace(s.group(1), new_hero + "\n        ")
    
    elif f == "jardines.html":
        s = re.search(r'(<section class="relative w-full h-\[600px\].*?</section>)', content, re.DOTALL)
        if s:
            bg = get_bg_url(s.group(1))
            inner = """                <span class="inline-block px-3 py-1 bg-primary rounded-full text-xs font-bold tracking-widest uppercase mb-4 text-white">Paisajismo Residencial</span>
                <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Transforma tu Hogar con Jardines Siempre Verdes</h1>
                <p class="text-white/80 max-w-2xl text-lg mb-6">Soluciones de paisajismo premium que combinan estética natural con durabilidad extrema.</p>
                <div class="flex gap-4">
                    <button class="bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-lg font-bold transition-all">Ver Modelos</button>
                    <button class="bg-white/10 hover:bg-white/20 backdrop-blur-md text-white border border-white/30 px-6 py-3 rounded-lg font-bold transition-all">Cotización</button>
                </div>"""
            new_hero = "<!-- Hero Section -->\n" + template.format(bg_url=bg, content=inner).replace("<!-- Hero Section -->\n", "")
            content = content.replace(s.group(1), new_hero)
            
    elif f == "insumos.html":
        s = re.search(r'(<!-- Hero Section -->.*?)(<main)', content, re.DOTALL)
        if s:
            bg = get_bg_url(s.group(1))
            inner = """                <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Todo para una Instalación Profesional</h1>
                <p class="text-white/80 max-w-2xl text-lg mb-6">Garantiza la durabilidad y el acabado perfecto de tu pasto sintético con insumos de alta calidad diseñados para resistir cualquier clima.</p>
                <button class="bg-primary text-white px-6 py-3 rounded-lg font-bold hover:bg-primary/90 transition-all">Ver Catálogo</button>"""
            new_hero = template.format(bg_url=bg, content=inner)
            content = content.replace(s.group(1), new_hero + "\n        ")

    elif f == "calculadora.html":
        s = re.search(r'(<section class="mb-12 text-center md:text-left">.*?</section>)', content, re.DOTALL)
        if s:
            bg = "https://lh3.googleusercontent.com/aida-public/AB6AXuCyvYjkhVnkhit5kjPRBh0ATEkF9T3JAlGxa-Kg_DlZeAPV4alHZJtdeqgEeK2bumqugIhRDtg4rqCAyqYfycpvmwCxw4S0VcOj3_3cKbamaljL1S2UuEpgF69l4V9dzYjdD763KcUSQy_mJBjhlzNVeURMS2-4wa71ENgAS-IRfdJB743cadgXLrPn9PzL8ebYVZMSOjpjFfeIvOUAfaFBjxW7CthLxWQJOEFGJ7__ovYWF75rcw9PVVLm9OVwqKT1cejYAdMpRsA"
            inner = """                <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Calculadora de Materiales</h1>
                <p class="text-white/80 max-w-2xl text-lg">Optimiza tu presupuesto y evita desperdicios calculando exactamente lo que necesitas.</p>"""
            new_hero = "<!-- Hero Section -->\n" + template.format(bg_url=bg, content=inner).replace("<!-- Hero Section -->\n", "")
            content = content.replace(s.group(1), new_hero)
            
    elif f == "contacto.html":
        s = re.search(r'(<section class="mb-12 text-center md:text-left">.*?</section>)', content, re.DOTALL)
        if s:
            bg = "https://lh3.googleusercontent.com/aida-public/AB6AXuDJXN_9HiC8inDu0BCD5K81Nkv14-nzdCkLnBcisK-O3kVGQhOn6zKooJ0sfjRbb1UaxKaeqfH3m7hY2o2vBo-INmmmoRydd3Skms_HUGV_gVRiIoVB5TImqGHjnhNFYQdJbbao2cD1o_HxW8b9_T8fpoN7oWhBPwlepi91zw1RBItDTCFX-rVBZ6yFMcO9__DJIgI57juZCF6gJK_qOhM-2yXpqisIsvROC6oR6yNWLqXUML0RM7dUN8Qg8wuXRlc3SK-lCmtEnI8"
            inner = """                <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Contacto Exclusivo</h1>
                <p class="text-white/80 max-w-2xl text-lg">Ponte en contacto con nosotros para cotizaciones, dudas o asesoría personalizada.</p>"""
            new_hero = "<!-- Hero Section -->\n" + template.format(bg_url=bg, content=inner).replace("<!-- Hero Section -->\n", "")
            content = content.replace(s.group(1), new_hero)

    with open(f, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Updated {f}")

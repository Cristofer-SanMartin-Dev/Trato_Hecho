import re
import os

seo_data = {
    "index.html": {
        "title": "Pasto Sintético Premium en Chile | Venta e Instalación",
        "desc": "Líderes en pasto sintético en Chile. Descubre nuestra calidad premium para jardines, canchas deportivas y terrazas. Cotiza tu proyecto con instalación profesional.",
        "url": "https://www.syntheticgrass.cl/"
    },
    "pasto-deportivo.html": {
        "title": "Pasto Sintético Deportivo y Canchas | Estándar FIFA",
        "desc": "Superficies de pasto sintético para canchas de fútbol, pádel y tenis. Rendimiento profesional, máxima durabilidad y certificaciones internacionales. Cotiza ahora.",
        "url": "https://www.syntheticgrass.cl/pasto-deportivo.html"
    },
    "jardines.html": {
        "title": "Pasto Sintético para Jardines y Paisajismo | Natural y Duradero",
        "desc": "Transforma tu hogar con nuestro césped sintético decorativo. Ideal para jardines, terrazas y paisajismo. Aspecto 100% natural, amigable con mascotas y libre de mantención.",
        "url": "https://www.syntheticgrass.cl/jardines.html"
    },
    "insumos.html": {
        "title": "Insumos para Instalar Pasto Sintético | Adhesivos y Rellenos",
        "desc": "Todo lo que necesitas para una instalación profesional de césped sintético: pegamento de poliuretano, cinta de unión, arena de sílice y caucho granulado.",
        "url": "https://www.syntheticgrass.cl/insumos.html"
    },
    "calculadora.html": {
        "title": "Calculadora de Materiales para Pasto Sintético | Presupuesto Exacto",
        "desc": "Optimiza tu compra con nuestra calculadora inteligente. Ingresa las medidas de tu terreno y descubre exactamente cuántos rollos, pegamento y arena necesitas.",
        "url": "https://www.syntheticgrass.cl/calculadora.html"
    },
    "contacto.html": {
        "title": "Contacto y Cotización Oficial | SyntheticGrass Chile",
        "desc": "¿Tienes dudas o quieres cotizar tu proyecto de pasto sintético? Contáctanos a través de nuestro formulario, WhatsApp o teléfono. Expertos a tu disposición.",
        "url": "https://www.syntheticgrass.cl/contacto.html"
    }
}

default_img = "https://lh3.googleusercontent.com/aida-public/AB6AXuCyvYjkhVnkhit5kjPRBh0ATEkF9T3JAlGxa-Kg_DlZeAPV4alHZJtdeqgEeK2bumqugIhRDtg4rqCAyqYfycpvmwCxw4S0VcOj3_3cKbamaljL1S2UuEpgF69l4V9dzYjdD763KcUSQy_mJBjhlzNVeURMS2-4wa71ENgAS-IRfdJB743cadgXLrPn9PzL8ebYVZMSOjpjFfeIvOUAfaFBjxW7CthLxWQJOEFGJ7__ovYWF75rcw9PVVLm9OVwqKT1cejYAdMpRsA"

files = ["index.html", "pasto-deportivo.html", "jardines.html", "insumos.html", "calculadora.html", "contacto.html"]

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading {f}: {e}")
        continue

    # Change lang attribute
    content = re.sub(r'<html\s+lang="[^"]+"', '<html lang="es-CL"', content)
    
    # Remove existing title tags
    content = re.sub(r'\s*<title>.*?</title>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove existing description tags
    content = re.sub(r'\s*<meta\s+name="description".*?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s*<meta\s+content="[^"]*"\s+name="description"\s*/?>', '', content, flags=re.IGNORECASE)
    
    # Remove existing canonical if any
    content = re.sub(r'\s*<link\s+rel="canonical".*?>', '', content, flags=re.IGNORECASE)
    
    # Remove existing OG or Twitter tags just in case
    content = re.sub(r'\s*<meta\s+property="og:.*?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s*<meta\s+name="twitter:.*?>', '', content, flags=re.IGNORECASE)

    data = seo_data.get(f, seo_data['index.html'])
    title = data['title']
    desc = data['desc']
    url = data['url']

    seo_block = f"""
    <!-- SEO Básico -->
    <title>{title}</title>
    <meta name="description" content="{desc}" />
    <meta name="keywords" content="pasto sintético, césped artificial, instalación de pasto, canchas deportivas, paisajismo, pasto sintético Chile, pasto decorativo" />
    <meta name="author" content="SyntheticGrass" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{url}" />

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:image" content="{default_img}" />
    <meta property="og:site_name" content="SyntheticGrass" />
    <meta property="og:locale" content="es_CL" />

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content="{url}" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{desc}" />
    <meta name="twitter:image" content="{default_img}" />
    """

    # Inject SEO block after viewport meta tag
    # First, let's normalize the viewport meta tag so we can match it predictably
    viewport_pattern = re.compile(r'<meta[^>]*name="viewport"[^>]*>', re.IGNORECASE)
    match = viewport_pattern.search(content)
    
    if match:
        end_idx = match.end()
        content = content[:end_idx] + "\n" + seo_block + content[end_idx:]
    else:
        # If no viewport, put it after head
        head_pattern = re.compile(r'<head>', re.IGNORECASE)
        match = head_pattern.search(content)
        if match:
             end_idx = match.end()
             content = content[:end_idx] + "\n" + seo_block + content[end_idx:]

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Added SEO to {f}")

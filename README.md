# Cesped Sintetico Pro 🌿

![Pasto Sinténtico Premium](https://lh3.googleusercontent.com/aida-public/AB6AXuCyvYjkhVnkhit5kjPRBh0ATEkF9T3JAlGxa-Kg_DlZeAPV4alHZJtdeqgEeK2bumqugIhRDtg4rqCAyqYfycpvmwCxw4S0VcOj3_3cKbamaljL1S2UuEpgF69l4V9dzYjdD763KcUSQy_mJBjhlzNVeURMS2-4wa71ENgAS-IRfdJB743cadgXLrPn9PzL8ebYVZMSOjpjFfeIvOUAfaFBjxW7CthLxWQJOEFGJ7__ovYWF75rcw9PVVLm9OVwqKT1cejYAdMpRsA)

Bienvenido al repositorio oficial de **Cesped Sintetico Pro**, la plataforma líder en soluciones de superficies sintéticas de alta gama en Chile. Este proyecto ofrece una experiencia web moderna, interactiva y optimizada para la cotización e instalación de pasto sintético residencial y deportivo.

## 🚀 Características Principales

-   **Diseño Premium e Interactivo**: Interfaz moderna construida con **Tailwind CSS**, soporte para **Modo Oscuro** y animaciones fluidas.
-   **🤖 Chatbot Experto "Queno"**: Asistente virtual inteligente integrado con un workflow de **n8n** para resolver dudas técnicos en tiempo real.
-   **📏 Calculadora Inteligente**: Herramienta avanzada para estimar materiales (m², adhesivo, arena de sílice y cinta de unión) según las dimensiones del proyecto.
-   **📄 Buscador de Documentos**: Interfaz para la consulta rápida de cotizaciones y estados de venta.
-   **📱 Totalmente Responsivo**: Optimizado para una visualización perfecta en dispositivos móviles, tablets y escritorio.
-   **🛠️ Automatización con Python**: Incluye una suite de scripts para mantenimiento de SEO, generación de documentos Word (.docx) y actualizaciones masivas de componentes.

## 🛠️ Stack Tecnológico

-   **Frontend**: HTML5, JavaScript (ES6+), Tailwind CSS.
-   **Herramientas de Diseño**: Google Fonts (Inter), Material Symbols.
-   **Backend/Integraciones**: n8n (Orquestación), Webhooks.
-   **Automatización**: Python 3.x (Scripts de mantenimiento y procesamiento de datos).

## 📂 Estructura del Proyecto

-   `index.html`: Página principal con el catálogo de productos y servicios.
-   `calculadora.html`: Herramienta de cálculo de materiales.
-   `documento.html`: Consulta de documentos y cotizaciones.
-   `pasto-deportivo.html`: Sección especializada en canchas profesionales.
-   `jardines.html`: Soluciones para paisajismo residencial.
-   `chatbot.js`: Lógica de interacción con el asistente virtual.
-   `scripts/` (Python):
    -   `generar_docx.py`: Automatización para la creación de reportes y presupuestos.
    -   `add_seo.py`: Inyección masiva de meta-etiquetas y optimización SEO.
    -   `update_n8n.py`: Gestión de conexiones con el motor de automatización.

## 💻 Instalación Local

1.  Clona este repositorio:
    ```bash
    git clone  https://github.com/AndresRomeroMadrid/TratoHecho
    ```
2.  Abre el proyecto en tu editor preferido (recomendado VS Code).
3.  Para visualizar la web, puedes usar la extensión **Live Server** o simplemente abrir `index.html` en tu navegador.
4.  Si deseas ejecutar los scripts de Python:
    ```bash
    pip install -r requirements.txt  # (Asegúrate de tener un entorno virtual activo)
    python script_name.py
    ```

## 🤖 Configuración del Chatbot

El chatbot "Queno" requiere una instancia de **n8n** activa. Para configurarlo:
1. Asegúrate de que n8n esté corriendo localmente o en un servidor.
2. Actualiza la URL del webhook en `chatbot.js` o usa el script `update_ngrok.py` si estás usando un túnel.


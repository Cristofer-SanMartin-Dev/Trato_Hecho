import os
import glob
import re

search_pattern = r"""    <!-- N8N Integration snippet -->
    <script>
        // Inicializa el chatbot embebido si tienes su librería inyectable externa.
        if \(window\.n8nChat && typeof window\.n8nChat\.init === 'function'\) \{
            window\.n8nChat\.init\(\{
                serverUrl: "http://localhost:5678"
            \}\);
        \}
    </script>"""

replace_pattern = """    <!-- N8N Integration snippet -->
    <script>
        window.n8nChat.init({
            // CAMBIA ESTO POR TU URL DE NGROK
            serverUrl: "https://marhta-unstubborn-minnie.ngrok-free.dev"
        });
    </script>"""

search_fetch = r"fetch\('http://localhost:5678/webhook/chat'"
replace_fetch = r"fetch('https://marhta-unstubborn-minnie.ngrok-free.dev/webhook/chat'"

for file_path in glob.glob("*.html"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = re.sub(search_pattern, replace_pattern, content)
    new_content = re.sub(search_fetch, replace_fetch, new_content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {file_path}")

import os

with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

# Extract script from index.html
start_marker = "    <script>\n        document.addEventListener('DOMContentLoaded', () => {\n            const chatbotButton = document.getElementById('chatbot-button');"
end_marker = "        });\n    </script>\n\n\n\n</body>"

start_idx = index_content.find(start_marker)
end_idx = index_content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find script markers in index.html")
    exit(1)

new_script = index_content[start_idx:end_idx + len("        });\n    </script>")]

files_to_update = [
    'contacto.html',
    'insumos.html',
    'jardines.html',
    'pasto-deportivo.html',
    'calculadora.html'
]

old_start_marker = "    <!-- Chatbot Logic -->\n    <script>\n        document.addEventListener('DOMContentLoaded', () => {\n            const chatbotButton = document.getElementById('chatbot-button');"
old_end_marker = "        });\n    </script>\n</body>"

for filename in files_to_update:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Step 1: Remove N8N integration snippet entirely
        start_n8n = content.find("    <!-- N8N Integration snippet -->")
        end_n8n_script = content.find("    </script>\n\n    <!-- Chatbot Logic -->")
        if start_n8n != -1 and end_n8n_script != -1:
            # We want to remove from start_n8n to end_n8n_script + len("    </script>\n\n")
            content = content[:start_n8n] + content[end_n8n_script + len("    </script>\n\n"):]

        # Step 2: Replace the Chatbot Logic
        start_logic = content.find("    <!-- Chatbot Logic -->\n    <script>")
        end_logic = content.find("        });\n    </script>\n</body>")
        
        if start_logic != -1 and end_logic != -1:
            content = content[:start_logic] + "    <!-- Chatbot Logic -->\n" + new_script + "\n</body>" + content[end_logic + len("        });\n    </script>\n</body>"):]
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated", filename)
        else:
            print("Could not find Chatbot Logic markers in", filename)

    except Exception as e:
        print("Error processing", filename, ":", str(e))

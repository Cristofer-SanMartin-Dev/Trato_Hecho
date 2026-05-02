const fs = require('fs');

const indexHtml = fs.readFileSync('index.html', 'utf8');

const startMarker = "    <script>\n        document.addEventListener('DOMContentLoaded', () => {\n            const chatbotButton = document.getElementById('chatbot-button');";
const endMarker = "        });\n    </script>\n\n\n\n</body>";

const startIndex = indexHtml.indexOf(startMarker);
const endIndex = indexHtml.indexOf(endMarker);

if (startIndex === -1 || endIndex === -1) {
    console.log("Could not find new script markers in index.html");
    process.exit(1);
}

// "});\n    </script>" is 15 characters
const newScript = indexHtml.substring(startIndex, endIndex + 15);

const filesToUpdate = [
    'contacto.html',
    'insumos.html',
    'jardines.html',
    'pasto-deportivo.html',
    'calculadora.html'
];

filesToUpdate.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');

    // 1. Remove <!-- N8N Integration snippet --> section (from 489 to 495 approx)
    let n8nStart = content.indexOf("    <!-- N8N Integration snippet -->\n    <script>\n        window.n8nChat.init({\n            // CAMBIA ESTO POR TU URL DE NGROK\n            serverUrl: \"https://marhta-unstubborn-minnie.ngrok-free.dev\"\n        });\n    </script>\n");
    if (n8nStart !== -1) {
        content = content.replace("    <!-- N8N Integration snippet -->\n    <script>\n        window.n8nChat.init({\n            // CAMBIA ESTO POR TU URL DE NGROK\n            serverUrl: \"https://marhta-unstubborn-minnie.ngrok-free.dev\"\n        });\n    </script>\n\n", "");
    }

    // 2. Replace the old Chatbot Logic
    let oldStart = content.indexOf("    <!-- Chatbot Logic -->\n    <script>\n        document.addEventListener('DOMContentLoaded', () => {");
    let oldEnd = content.indexOf("        });\n    </script>\n</body>");

    if (oldStart !== -1 && oldEnd !== -1) {
        content = content.substring(0, oldStart) + "    <!-- Chatbot Logic -->\n" + newScript + "\n</body>" + content.substring(oldEnd + 33);
        fs.writeFileSync(file, content, 'utf8');
        console.log("Updated " + file);
    } else {
        console.log("Could not find old markers in " + file);
    }
});

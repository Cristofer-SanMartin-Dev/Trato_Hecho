const fs = require('fs');

const indexHtml = fs.readFileSync('index.html', 'utf8');
const startStr = "    <script>\n        document.addEventListener('DOMContentLoaded', () => {";
const endStr = "    </script>\n\n\n\n</body>";

let startIdx = indexHtml.indexOf(startStr);
let endIdx = indexHtml.indexOf(endStr);
const newScript = indexHtml.substring(startIdx, endIdx + 13); // up to </script>

const filesToUpdate = ['contacto.html', 'insumos.html', 'jardines.html', 'pasto-deportivo.html', 'calculadora.html'];

for (let file of filesToUpdate) {
    let content = fs.readFileSync(file, 'utf8');

    // Strip out N8N integration block
    let startN8N = content.indexOf('    <!-- N8N Integration snippet -->');
    let endN8N = content.indexOf('    </script>\n\n    <!-- Chatbot Logic -->');
    if (startN8N > -1 && endN8N > -1) {
        content = content.substring(0, startN8N) + content.substring(endN8N + 15);
    }

    // Swap the main chatbot logic block
    let oldStart = content.indexOf("    <!-- Chatbot Logic -->\n    <script>\n        document.addEventListener('DOMContentLoaded', () => {");
    let oldEnd = content.indexOf("        });\n    </script>\n</body>");

    if (oldStart !== -1 && oldEnd !== -1) {
        let beforeContent = content.substring(0, oldStart);
        let afterContent = content.substring(oldEnd + 33); // "        });\n    </script>\n</body>" length approx

        // rebuild
        let result = beforeContent + "    <!-- Chatbot Logic -->\n" + newScript + "\n</body>\n</html>";
        fs.writeFileSync(file, result, 'utf8');
        console.log("Updated", file);
    } else {
        console.log("Could not update", file);
    }
}

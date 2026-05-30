const fs = require('fs');
const glob = require('glob');

const searchPattern = `    <!-- N8N Integration snippet -->
    <script>
        // Inicializa el chatbot embebido si tienes su librería inyectable externa.
        if (window.n8nChat && typeof window.n8nChat.init === 'function') {
            window.n8nChat.init({
                serverUrl: "http://localhost:5678"
            });
        }
    </script>`;

const replacePattern = `    <!-- N8N Integration snippet -->
    <script>
        window.n8nChat.init({
            // CAMBIA ESTO POR TU URL DE NGROK
            serverUrl: "https://marhta-unstubborn-minnie.ngrok-free.dev"
        });
    </script>`;

const searchFetch = `fetch('http://localhost:5678/webhook/chat'`;
const replaceFetch = `fetch('https://marhta-unstubborn-minnie.ngrok-free.dev/webhook/chat'`;

const files = ['index.html', 'contacto.html', 'insumos.html', 'jardines.html', 'pasto-deportivo.html', 'calculadora.html'];

files.forEach(file => {
    try {
        let content = fs.readFileSync(file, 'utf8');

        let newContent = content.replace(searchPattern, replacePattern);
        // También actualizamos la llamada a fetch de nuestra UI custom para que siga funcionando con ngrok
        newContent = newContent.replace(searchFetch, replaceFetch);

        if (newContent !== content) {
            fs.writeFileSync(file, newContent, 'utf8');
            console.log(`Updated ngrok url in ${file}`);
        }
    } catch (e) {
        console.log(`Error updating ${file}: ${e.message}`);
    }
});

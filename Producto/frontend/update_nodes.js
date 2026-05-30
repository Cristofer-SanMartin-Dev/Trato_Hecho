const fs = require('fs');

const indexHtml = fs.readFileSync('index.html', 'utf8');

const regex = /<script>[\s\S]*?document\.addEventListener\('DOMContentLoaded', \(\) => \{[\s\S]*?const chatbotButton = document\.getElementById\('chatbot-button'\);[\s\S]*?<\/script>/;

const match = indexHtml.match(regex);
if (!match) {
    console.log('Could not find the script in index.html');
    process.exit(1);
}

const newScript = match[0];

const filesToUpdate = [
    'contacto.html',
    'insumos.html',
    'jardines.html',
    'pasto-deportivo.html',
    'calculadora.html'
];

filesToUpdate.forEach(file => {
    try {
        let content = fs.readFileSync(file, 'utf8');

        let targetRegex = /<!-- Chatbot Logic -->\s*<script>[\s\S]*?document\.addEventListener\('DOMContentLoaded', \(\) => \{[\s\S]*?const chatbotButton = document\.getElementById\('chatbot-button'\);[\s\S]*?<\/script>/;

        if (targetRegex.test(content)) {
            content = content.replace(targetRegex, `<!-- Chatbot Logic -->\n    ${newScript}`);
        } else {
            let backupRegex = /<script>[\s\S]*?document\.addEventListener\('DOMContentLoaded', \(\) => \{[\s\S]*?const chatbotButton = document\.getElementById\('chatbot-button'\);[\s\S]*?<\/script>/;
            if (backupRegex.test(content)) {
                content = content.replace(backupRegex, newScript);
            }
        }

        // Clean old integration
        let iniSnippetRegex = /<!-- N8N Integration snippet -->\s*<script>[\s\S]*?window\.n8nChat\.init\(\{[\s\S]*?\}\);\s*<\/script>/;
        if (iniSnippetRegex.test(content)) {
            content = content.replace(iniSnippetRegex, '');
        }

        fs.writeFileSync(file, content, 'utf8');
        console.log('Updated ' + file);
    } catch (err) {
        console.log('Error on ' + file, err);
    }
});

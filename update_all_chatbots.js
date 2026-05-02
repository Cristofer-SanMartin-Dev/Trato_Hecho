const fs = require('fs');

const indexHtml = fs.readFileSync('index.html', 'utf8');

const regex = /<script>[\s\S]*?document\.addEventListener\('DOMContentLoaded', \(\) => \{[\s\S]*?const chatbotButton = document\.getElementById\('chatbot-button'\);[\s\S]*?<\/script>/;

const match = indexHtml.match(regex);
if (!match) {
    console.error('Could not find the script in index.html');
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
    let content = fs.readFileSync(file, 'utf8');

    // In old files, the script starts with <script> and ends with </script> but it also has <!-- Chatbot Logic --> just before it.
    // Let's replace the script that starts with <!-- Chatbot Logic -->\n    <script> document.addEventListener('DOMContentLoaded'

    // The old files still have the <!-- N8N Integration snippet -->
    // We should probably just replace the old DOMContentLoaded script.

    const targetRegex = /<!-- Chatbot Logic -->\s*<script>[\s\S]*?document\.addEventListener\('DOMContentLoaded', \(\) => \{[\s\S]*?const chatbotButton = document\.getElementById\('chatbot-button'\);[\s\S]*?<\/script>/;

    if (targetRegex.test(content)) {
        content = content.replace(targetRegex, `<!-- Chatbot Logic -->\n    ${newScript}`);
        fs.writeFileSync(file, content, 'utf8');
        console.log(`Updated ${file}`);
    } else {
        console.error(`Could not find the target script in ${file} with <!-- Chatbot Logic -->`);

        // Try without <!-- Chatbot Logic --> prefix
        const backupRegex = /<script>[\s\S]*?document\.addEventListener\('DOMContentLoaded', \(\) => \{[\s\S]*?const chatbotButton = document\.getElementById\('chatbot-button'\);[\s\S]*?<\/script>/;
        if (backupRegex.test(content)) {
            content = content.replace(backupRegex, newScript);
            fs.writeFileSync(file, content, 'utf8');
            console.log(`Updated ${file} (fallback regex)`);
        } else {
            console.error(`COULD NOT FIND ANY MATCH IN ${file}`);
        }
    }

    // Oh, also the user removed <!-- N8N Integration snippet --> and window.n8nChat.init block completely from index.html in their own paste.
    // Let's strip it out from the other files too, so everything matches exactly.
    const iniSnippetRegex = /<!-- N8N Integration snippet -->\s*<script>[\s\S]*?window\.n8nChat\.init\(\{[\s\S]*?\}\);\s*<\/script>/;
    if (iniSnippetRegex.test(content)) {
        content = content.replace(iniSnippetRegex, '');
        fs.writeFileSync(file, content, 'utf8');
        console.log(`Cleaned old n8nChat.init snippet from ${file}`);
    }

});

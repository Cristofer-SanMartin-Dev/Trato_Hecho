import re
import os

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

header_match = re.search(r'<header.*?</header>', content, flags=re.DOTALL)
if not header_match:
    print('No header found in index.html')
    exit(1)

new_header = header_match.group(0)

files = ['pasto-deportivo.html', 'jardines.html', 'insumos.html', 'calculadora.html', 'contacto.html']
for fn in files:
    with open(fn, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Using string replace instead of regex sub for simplicity to avoid escape issues
    start_idx = file_content.find('<header')
    end_idx = file_content.find('</header>') + len('</header>')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        file_content = file_content[:start_idx] + new_header + file_content[end_idx:]
        
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f'Replaced header in {fn}')
    else:
        print(f'Header tag missing in {fn}')

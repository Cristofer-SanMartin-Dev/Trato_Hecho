import re

files = ["index.html", "jardines.html", "insumos.html", "calculadora.html", "contacto.html", "pasto-deportivo.html"]

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        continue
        
    # Replace the w-16 h-16 with w-[72px] h-[72px] or w-20 h-20. Let's use w-[72px] h-[72px] to make it slightly larger (from 64 to 72)
    new_content = content.replace(
        'w-16 h-16 rounded-full', 
        'w-[76px] h-[76px] rounded-full'
    )
    
    # Also let's enlarge the online dot just a bit to match
    new_content = new_content.replace(
        'w-4 h-4 bg-green-500 border-2',
        'w-5 h-5 bg-green-500 border-[3px]'
    )
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {f}")

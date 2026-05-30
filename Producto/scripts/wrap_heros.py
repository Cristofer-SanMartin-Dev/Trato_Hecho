import re

files = ['index.html', 'jardines.html', 'insumos.html', 'calculadora.html', 'contacto.html']
for f in files:
    try:
        content = open(f, encoding='utf-8').read()
    except: continue
    
    # We want to match:
    # <!-- Hero Section -->
    # <section class="relative rounded-xl overflow-hidden mb-12 min-h-[300px] flex items-end">
    # ...
    # </section>
    
    pattern = r'(<!-- Hero Section -->\s*<section class="relative rounded-xl overflow-hidden mb-12 min-h-\[300px\] flex items-end">.*?</section>)'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        hero = m.group(1)
        # Check if already wrapped
        before_hero = content[:m.start()]
        if 'max-w-7xl' not in before_hero[-200:]:
            wrapped_hero = f'<div class="max-w-7xl mx-auto px-4 md:px-8 mt-8 w-full">\n    {hero}\n</div>'
            content = content[:m.start()] + wrapped_hero + content[m.end():]
            open(f, 'w', encoding='utf-8').write(content)
            print('Wrapped hero in', f)
        else:
            print(f, 'already wrapped')
    else:
        print('Hero not found in', f)

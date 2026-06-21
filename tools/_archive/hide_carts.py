import re
import glob

files = ["index.html", "jardines.html", "insumos.html", "calculadora.html", "contacto.html", "pasto-deportivo.html"]

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading {f}: {e}")
        continue
        
    # 1. Hide the header shopping cart button
    # Pattern: match exactly the button containing shopping_cart.
    # We look for <button class="..."...> then some space, then <span ...>shopping_cart</span>
    # Notice the cart might have <span class="absolute ... text-[10px] font-bold">3</span> below it
    
    # We can match `<button` followed by everything up to `shopping_cart</span>`, find the class attribute and inject 'hidden'.
    
    def replacer_header(m):
        btn_start = m.group(1) # '<button'
        attrs = m.group(2) # attributes before class
        cls = m.group(3) # class="..."
        rest = m.group(4) # rest up to shopping_cart
        
        if 'hidden' not in cls:
            # Insert hidden into the class
            new_cls = cls.replace('class="', 'class="hidden ')
            return btn_start + attrs + new_cls + rest
        return m.group(0)

    # Let's use a simpler regex that matches the button element containing shopping_cart directly if we can
    # But python regex with .*? is fine.
    # Find all <button ... shopping_cart</span> 
    # Use re.sub with a function
    pattern_cart = r'(<button)([\s]*class=")([^"]*)("\s*>\s*<span[^>]*>[^<]*shopping_cart\s*</span>)'
    content = re.sub(pattern_cart, lambda m: f'{m.group(1)}{m.group(2)}hidden {m.group(3)}{m.group(4)}' if 'hidden' not in m.group(3) else m.group(0), content)
    
    # Also for add_shopping_cart. These might also be a button or an anchor (usually button)
    pattern_add_cart = r'(<button)([^>]*class=")([^"]*)("[^>]*>\s*<span[^>]*>[^<]*add_shopping_cart\s*</span>)'
    content = re.sub(pattern_add_cart, lambda m: f'{m.group(1)}{m.group(2)}hidden {m.group(3)}{m.group(4)}' if 'hidden' not in m.group(3) else m.group(0), content)
    
    # In calculadora, there is the big button:
    # <button class="flex w-full ..."> <span ...>add_shopping_cart</span> AÑADIR MATERIALES ... </button>
    pattern_calc = r'(<button)([^>]*class=")([^"]*)("[^>]*>\s*<span[^>]*>\s*add_shopping_cart\s*</span>\s*AÑADIR MATERIALES AL CARRITO\s*</button>)'
    content = re.sub(pattern_calc, lambda m: f'{m.group(1)}{m.group(2)}hidden {m.group(3)}{m.group(4)}' if 'hidden' not in m.group(3) else m.group(0), content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")

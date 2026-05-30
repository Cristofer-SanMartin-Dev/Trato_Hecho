"""Fix encoding issues in HTML files - detect and fix properly"""
import os

def fix_html_encoding(filepath):
    """Read file and fix encoding issues"""
    try:
        # Try reading as UTF-8 first (current state)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix double-encoded UTF-8 (UTF-8 bytes misinterpreted as Latin-1)
        # This happens when UTF-8 text is saved/read as Latin-1
        content_bytes = content.encode('latin-1')
        content_fixed = content_bytes.decode('utf-8')
        
        # Write back as proper UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_fixed)
        
        print(f"✓ Fixed: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Error fixing {filepath}: {e}")
        return False

if __name__ == "__main__":
    # Fix index.html
    fix_html_encoding('index.html')
    
    # Fix other HTML files
    html_files = [
        'calculadora.html',
        'contacto.html',
        'documento.html',
        'insumos.html',
        'jardines.html',
        'pasto-deportivo.html'
    ]
    
    for html_file in html_files:
        if os.path.exists(html_file):
            fix_html_encoding(html_file)
    
    print("\n✓ Encoding fix completed!")

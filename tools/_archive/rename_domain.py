import glob

files = ["index.html", "pasto-deportivo.html", "jardines.html", "insumos.html", "calculadora.html", "contacto.html"]

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace URLs/domains
        content = content.replace('syntheticgrass.cl', 'cespedcintetico.cl')
        content = content.replace('syntheticturf.com', 'cespedcintetico.cl')
        
        # Replace brand names
        content = content.replace('SyntheticGrass', 'Cesped Sintetico')
        content = content.replace('SyntheticTurf', 'Cesped Sintetico')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"Updated {f}")
    except Exception as e:
        print(f"Error {f}: {e}")

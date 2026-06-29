import os
import glob

for file_path in glob.glob("*.html"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply changes
    if "Asesor Experto" in content:
        content = content.replace("Asesor Experto", " Queno")
        content = content.replace('alt="Asesor"', 'alt=" Queno"')
        content = content.replace("Soy tu asesor experto en césped sintético.", "Soy  Queno, tu asesor experto en césped sintético.")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes needed for {file_path}")

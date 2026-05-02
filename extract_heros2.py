import glob

with open("heros.txt", "w", encoding="utf-8") as out:
    for f in glob.glob("*.html"):
        content = open(f, encoding="utf-8").read()
        if "<!-- Hero Section -->" in content:
            parts = content.split("<!-- Hero Section -->")
            if len(parts) > 1:
                hero = parts[1][:2500]  # Take next 2500 chars which should cover the hero section
                out.write(f"\n====================== {f} ======================\n")
                out.write(hero + "\n")

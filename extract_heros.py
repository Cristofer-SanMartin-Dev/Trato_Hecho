import glob
import re

with open("heros.txt", "w", encoding="utf-8") as out:
    for f in glob.glob("*.html"):
        content = open(f, encoding="utf-8").read()
        match = re.search(r'(<!-- Hero Section -->.*?)(<!-- \w|<div class="grid |<main)', content, re.DOTALL | re.IGNORECASE)
        if match:
            out.write(f"\n====================== {f} ======================\n")
            out.write(match.group(1).strip() + "\n")

import sys
import re

files = ['index.html', 'jardines.html', 'insumos.html']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We are replacing:
    # <div class="max-w-7xl mx-auto px-4 md:px-8 mt-8 w-full">
    #     <!-- Hero Section -->
    #       ...
    #     </section>
    # </div>
    
    # Let's match the exact opening div of the hero wrapper:
    pattern_open = r'<div class=\"max-w-7xl mx-auto px-4 md:px-8 mt-8 w-full\">\s*(<!-- Hero Section -->)'
    new_open = r'<div class="px-6 mt-8 w-full">\n    <div class="mx-auto max-w-7xl">\n        \1'
    
    if re.search(pattern_open, content):
        # We need to add an extra </div> to the end of the hero section.
        # Find the start of the match
        match = re.search(pattern_open, content)
        # Find the closing </section> after the match
        section_end_match = re.search(r'</section>\s*</div>', content[match.end():])
        
        if section_end_match:
            # Replace opening
            content = re.sub(pattern_open, new_open, content, count=1)
            # Find the new closing spot and replace we just replace `</section> \n</div>` with `</section>\n</div>\n</div>` globally if it follows the hero but easier to just use string matching:
            # Let's instead use a single sub on the whole block
            block_pattern = r'(<div class="max-w-7xl mx-auto px-4 md:px-8 mt-8 w-full">\s*<!-- Hero Section -->\s*<section.*?flex items-end\">.*?</section>\s*)</div>'
            replacement = r'<div class="px-6 mt-8 w-full">\n    <div class="mx-auto max-w-7xl">\n        \1</div>\n</div>'
            # The capture group \1 will not capture `</div>` because the regex strips it out to be replaced
            # Wait, the \1 captures `<div class="...">\n <!-- Hero Section -->...`. We don't want the outer div in \1.
            
            # Better way:
            content = content.replace('<div class="max-w-7xl mx-auto px-4 md:px-8 mt-8 w-full">', '<div class="px-6 mt-8 w-full">\n    <div class="mx-auto max-w-7xl">', 1)
            
            # Now we add a </div> right after the hero's </section> that is followed by </div>.
            # To be safe, we just replace the exact chunk:
            idx = content.find('<!-- Hero Section -->')
            idx_sec_end = content.find('</section>', idx)
            idx_div_end = content.find('</div>', idx_sec_end)
            if idx_div_end != -1:
                content = content[:idx_div_end] + '</div>\n</div>' + content[idx_div_end+6:]
                
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print("Fixed", f)
        else:
            print("Couldn't find section end match in", f)
    else:
        print("Couldn't find pattern in", f)

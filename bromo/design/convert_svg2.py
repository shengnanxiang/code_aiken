from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os

svg_dir = r'C:/Users/Nan/Documents/GitHub/code_aiken/bromo/design'
views = ['FRONT', 'BACK', 'TOP', 'BOTTOM', 'LEFT', 'RIGHT']

for view in views:
    svg_path = os.path.join(svg_dir, f'Bromo-{view}.svg')
    png_path = os.path.join(svg_dir, f'Bromo-{view}.png')
    
    if os.path.exists(svg_path):
        try:
            drawing = svg2rlg(svg_path)
            renderPM.drawToFile(drawing, png_path, fmt='PNG')
            print(f'Converted: Bromo-{view}.svg -> Bromo-{view}.png')
        except Exception as e:
            print(f'Error converting {view}: {e}')
    else:
        print(f'Missing: {svg_path}')

print('Done.')

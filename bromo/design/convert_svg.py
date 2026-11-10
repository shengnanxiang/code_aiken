import cairosvg
import os

svg_dir = r'C:/Users/Nan/Documents/GitHub/code_aiken/bromo/design'
views = ['FRONT', 'BACK', 'TOP', 'BOTTOM', 'LEFT', 'RIGHT']

for view in views:
    svg_path = os.path.join(svg_dir, f'Bromo-{view}.svg')
    png_path = os.path.join(svg_dir, f'Bromo-{view}.png')
    
    if os.path.exists(svg_path):
        try:
            cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=2400, output_height=1800)
            print(f'Converted: Bromo-{view}.svg -> Bromo-{view}.png')
        except Exception as e:
            print(f'Error converting {view}: {e}')
    else:
        print(f'Missing: {svg_path}')

print('Done.')

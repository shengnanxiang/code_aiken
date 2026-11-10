from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import os

def svg_to_png(svg_path, png_path, scale=2):
    """Convert SVG to PNG using PIL (basic shapes only)"""
    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Get viewBox
    viewbox = root.get('viewBox', '0 0 1200 900').split()
    width = int(float(viewbox[2]))
    height = int(float(viewbox[3]))
    
    # Create image
    img = Image.new('RGB', (width * scale, height * scale), 'white')
    draw = ImageDraw.Draw(img)
    
    # Process elements
    for elem in root:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        
        if tag == 'rect':
            x = float(elem.get('x', 0)) * scale
            y = float(elem.get('y', 0)) * scale
            w = float(elem.get('width', 0)) * scale
            h = float(elem.get('height', 0)) * scale
            rx = float(elem.get('rx', 0)) * scale
            ry = float(elem.get('ry', 0)) * scale
            
            stroke = elem.get('stroke', '#000000')
            stroke_width = float(elem.get('stroke-width', 1)) * scale
            fill = elem.get('fill', 'none')
            dasharray = elem.get('stroke-dasharray', '')
            
            # Draw rectangle
            if rx > 0 or ry > 0:
                # Rounded rectangle (approximate with regular rect for now)
                draw.rectangle([x, y, x + w, y + h], outline=stroke, width=int(stroke_width))
            else:
                draw.rectangle([x, y, x + w, y + h], outline=stroke, width=int(stroke_width))
        
        elif tag == 'circle':
            cx = float(elem.get('cx', 0)) * scale
            cy = float(elem.get('cy', 0)) * scale
            r = float(elem.get('r', 0)) * scale
            
            stroke = elem.get('stroke', '#000000')
            stroke_width = float(elem.get('stroke-width', 1)) * scale
            
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=stroke, width=int(stroke_width))
        
        elif tag == 'line':
            x1 = float(elem.get('x1', 0)) * scale
            y1 = float(elem.get('y1', 0)) * scale
            x2 = float(elem.get('x2', 0)) * scale
            y2 = float(elem.get('y2', 0)) * scale
            
            stroke = elem.get('stroke', '#000000')
            stroke_width = float(elem.get('stroke-width', 1)) * scale
            
            draw.line([(x1, y1), (x2, y2)], fill=stroke, width=int(stroke_width))
        
        elif tag == 'text':
            x = float(elem.get('x', 0)) * scale
            y = float(elem.get('y', 0)) * scale
            text = elem.text or ''
            fill = elem.get('fill', '#000000')
            font_size = int(float(elem.get('font-size', 12)) * scale)
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            draw.text((x, y), text, fill=fill, font=font)
        
        elif tag == 'polygon':
            points_str = elem.get('points', '')
            if points_str:
                points = [(float(p.split(',')[0]) * scale, float(p.split(',')[1]) * scale) 
                         for p in points_str.split()]
                stroke = elem.get('stroke', '#000000')
                stroke_width = float(elem.get('stroke-width', 1)) * scale
                draw.polygon(points, outline=stroke, width=int(stroke_width))
    
    img.save(png_path, 'PNG')
    print(f'Converted: {svg_path} -> {png_path}')

# Process all views
svg_dir = r'C:/Users/Nan/Documents/GitHub/code_aiken/bromo/design'
views = ['FRONT', 'BACK', 'TOP', 'BOTTOM', 'LEFT', 'RIGHT']

for view in views:
    svg_path = os.path.join(svg_dir, f'Bromo-{view}.svg')
    png_path = os.path.join(svg_dir, f'Bromo-{view}.png')
    
    if os.path.exists(svg_path):
        try:
            svg_to_png(svg_path, png_path, scale=2)
        except Exception as e:
            print(f'Error converting {view}: {e}')
    else:
        print(f'Missing: {svg_path}')

print('Done.')

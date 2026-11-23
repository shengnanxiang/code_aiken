# -*- coding: utf-8 -*-
import json, collections, sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

p = r'C:\Users\Nan\.jiuwenswarm\agent\sessions\web_1a13db569b6_ccb2c0c0ee76\uploads\微信图片_20261119120100_8963_486.jpg'
out_path = r'C:\Users\Nan\Documents\GitHub\code_aiken\_img_meta_tmp.json'

img = Image.open(p)
small = img.convert('RGB').resize((100, 100))
pixels = list(small.getdata())
quant = [((r//32)*32, (g//32)*32, (b//32)*32) for r, g, b in pixels]
top = collections.Counter(quant).most_common(10)
lum = [0.299*r+0.587*g+0.114*b for r, g, b in pixels]

# 左右半区与上下半区的主色（判断构图重心）
w, h = 100, 100
def zone_color(x0, x1, y0, y1):
    zone = [pixels[y*w+x] for y in range(y0, y1) for x in range(x0, x1)]
    rq = sum(r for r, g, b in zone) // len(zone)
    gq = sum(g for r, g, b in zone) // len(zone)
    bq = sum(b for r, g, b in zone) // len(zone)
    return '#%02x%02x%02x' % (rq, gq, bq)

out = {
    'size': list(img.size),
    'exif': bool(img._getexif()),
    'top_colors': [['#%02x%02x%02x' % (c[0], c[1], c[2]), round(n/100.0, 2)] for c, n in top],
    'dark_pct': round(sum(1 for v in lum if v < 50)/100.0, 2),
    'bright_pct': round(sum(1 for v in lum if v > 200)/100.0, 2),
    'zone_avg': {
        'left_half': zone_color(0, 50, 0, 100),
        'right_half': zone_color(50, 100, 0, 100),
        'top_half': zone_color(0, 100, 0, 50),
        'bottom_half': zone_color(0, 100, 50, 100),
        'center': zone_color(30, 70, 30, 70),
    }
}
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('OK written')

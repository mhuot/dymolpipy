from PIL import Image, ImageDraw, ImageFont
import os
from textwrap3 import fill

img = Image.new('1', (1051,1051), 255) # 148?

font = ImageFont.truetype('/usr/share/fonts/truetype/tahoma.ttf', 105)
mytext = fill("12345678901234567890123456789012345678901234567890", 17)

d = ImageDraw.Draw(img)
d.text((0,0), mytext, font=font)
rotated = img.rotate(270)
rotated = rotated.crop( (1051-331, 0, 1051, 1051) )

rotated.save('./output/rotated.png')
img.save('./output/image.png', fillcolor="white")
os.system(f"lpr -o ppi=300 ./output/rotated.png")

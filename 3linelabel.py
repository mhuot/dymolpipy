from PIL import Image, ImageDraw, ImageFont
import os

img = Image.new('1', (1051,1051), 255) # 148?

font = ImageFont.truetype('/usr/share/fonts/truetype/tahoma.ttf', 105)

d = ImageDraw.Draw(img)
d.text((0,0), "a0123456789012345\nb01234567890\nc0123456789\n", font=font)
rotated = img.rotate(270)
rotated = rotated.crop( (1051-331, 0, 1051, 1051) )

rotated.save('./output/rotated.png')
img.save('./output/image.png', fillcolor="white")
os.system(f"lpr -o ppi=300 ./output/rotated.png")

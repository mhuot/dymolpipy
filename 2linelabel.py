from PIL import Image, ImageDraw, ImageFont
import os
from textwrap3 import fill

# xdimension = 1051
xdimension = 970
ydimension = 331
img = Image.new('1', (xdimension,xdimension), 255) # 148?

fontsize = 105
fontfile = '/System/Library/Fonts/Supplemental/Tahoma.ttf'
# fontfile = '/usr/share/fonts/truetype/tahoma.ttf'
font = ImageFont.truetype(fontfile, fontsize)
width = 0
printable = ""
# labelContent = fill("12345678901234567890123456789012345678901234567890", 17)
# labelContent = "12345678901234567890123456789012345678901234567890"
labelContent = "aBcdaedlkasjndfoinasdjnaskjdJDISNAKJSDKJNjnjasncadsjkansjidnijasniunJNJN"
line = 0
lines = []
for index in range(len(labelContent)) :
    currentchar = labelContent[index]
    if font.getsize(printable + currentchar)[0] <= xdimension:
        printable = printable + currentchar
    else:
        printable = printable + currentchar
        line += 1
        lines.append(printable)
        printable = ""

print(line)
lines.append(printable)

print("\n".join(lines))

d = ImageDraw.Draw(img)
d.text((0,0), mytext, font=font)
rotated = img.rotate(270)
rotated = rotated.crop( (xdimension-ydimension, 0, xdimension, xdimension) )

rotated.save('./output/rotated.png')
img.save('./output/image.png', fillcolor="white")
# os.system(f"lpr -o ppi=300 ./output/rotated.png")

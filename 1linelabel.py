from PIL import Image, ImageDraw, ImageFont
import os
import sys

arguments = len(sys.argv) - 1

position = 1
dry = False
while (arguments >= position):
	if sys.argv[position] == "--dry" or sys.argv[position] == "-d":
		dry = True
	position = position + 1

output = "./output"
length = 986
width = 331
fontsize = 300
img = Image.new('1', (length,length), 255) # Length is 1051 so we make a square of it and then we can rotate into a rectangle that is 1051x331

#font = ImageFont.truetype('/usr/share/fonts/truetype/tahoma.ttf', 305) # Nice but not monospaced
#font = ImageFont.truetype('/usr/share/fonts/truetype/VCR_OSD_MONO_1.001.ttf', 305) # To blocky
#font = ImageFont.truetype("/usr/share/fonts/truetype/Space Mono Nerd Font Complete Mono.ttf", 305) 
#font = ImageFont.truetype("/usr/share/fonts/truetype/Roboto Mono Nerd Font Complete Mono.ttf", 305) #Very nice but too much kerning
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fontsize) # System font so easy to deal with

d = ImageDraw.Draw(img)
d.text((0,0), "012345", font=font)
rotated = img.rotate(270) 
rotated = rotated.crop( (length-width, 0, length, length) ) # Getting to the 1051x331 rectangle

rotated.save(f"{output}/rotated.png")
# img.save('f"{output}/image.png", fillcolor="white") # Only needed for debugging
if not dry:
	os.system(f"lpr -o ppi=300 {output}/rotated.png")

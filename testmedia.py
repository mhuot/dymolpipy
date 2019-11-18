from PIL import Image, ImageDraw, ImageFont
import os
from time import sleep

font = ImageFont.truetype('/usr/share/fonts/truetype/tahoma.ttf', 50)
media = open('media.txt', "r")

for medium in media:
	img = Image.new('1', (760,760), 255) # 148?
	d = ImageDraw.Draw(img)
	print(f"Starting {medium.strip()}")
	d.text((0,0), f"Hello!!!\nHello2\nHello3\nHello4\n{medium.strip()}\nHello6\nHello7\nHello8\nHello9\nHello10\nHello11", font=font)
	rotated = img.rotate(270)
	rotated = rotated.crop( (350, 0, 760, 760) )
	rotated.save(f"./output/{medium.strip()}-rotated.png")
	img.save(f"./output/{medium.strip()}.png", fillcolor="white")

	command = f"lpr -o media={medium.strip()} -o ppi=300 -o PrintQuality=Graphics ./output/{medium.strip()}-rotated.png"
	print(f"Sending {command}")
	os.system(command)
	print(f"Ending {medium.strip()}")
	input("Press Enter to continue...")

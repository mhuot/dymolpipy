import os
from time import sleep

media = open('media.txt', "r")

for medium in media:
	command = f"lpr -o media={medium.strip()} -o ppi=300 -o PrintQuality=Graphics ../dymo-cups-drivers-1.4.0.5/docs/TestImage.png"
	print(f"Sending {command}")
	os.system(command)
	print(f"Ending {medium.strip()}")
	input("Press Enter to continue...")

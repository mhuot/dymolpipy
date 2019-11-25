from PIL import Image, ImageDraw, ImageFont
import os

# xdimension = 1051
xdimension = 970
ydimension = 331
img = Image.new('1', (xdimension,xdimension), 255) # 148?

# fontsize = 100 # Three Lines
# fontsize = 300 # One Line
# fontsize = 150 # Two lines?
fontsizes = [ 100, 150, 300 ]

fontfile = '/System/Library/Fonts/Supplemental/Tahoma.ttf'
# fontfile = '/usr/share/fonts/truetype/tahoma.ttf'
width = 0
printable = ""
# labelContent = fill("12345678901234567890123456789012345678901234567890", 17)
# labelContent = "12345678901234567890123456789012345678901234567890"
labelContent = "First second third fouth fifth Sixth Seventh eighth nineth tenth"
labelContent = "Test second"
labelWords = labelContent.split()

lines = []
testing = ""
maxlines = 3
linenumber = 0

for size in fontsizes:
    lines = []
    for word in labelWords:
        print(f"Checking on word {word}")
        font = ImageFont.truetype(fontfile, size)
        if lines: # See if we have any lines yet, if we do then let's check the length plus our new word
            currentline = lines[linenumber] + " " + word
        else: # No lines yet so we only need to see if our word fits on the line
            currentline = word
        if font.getsize(currentline)[0] < xdimension:
            print(f"Looking at line {linenumber}")
            if lines:
                if lines[linenumber]:
                    print(f"Reseting {linenumber} of {lines[linenumber]} to {currentline}")
                    lines[linenumber] = testing
                else:
                    lines.append(currentline)
            else:
                print(f"Appending {currentline}")
                lines.append(currentline)
        else:
            if len(lines) <= 2:
                print(f"Adding line {linenumber} with {testing}")
                lines.append(testing)
            linenumber += 1
            if linenumber == maxlines:
                break
            testing = ""

# print(lines)
# lines.append(printable)

mytext = "\n".join(lines)
print(f"Here is our - \n\n{mytext}")


d = ImageDraw.Draw(img)
d.text((0,0), mytext, font=font)
rotated = img.rotate(270)
rotated = rotated.crop( (xdimension-ydimension, 0, xdimension, xdimension) )

rotated.save('./output/rotated.png')
img.save('./output/image.png', fillcolor="white")
# os.system(f"lpr -o ppi=300 ./output/rotated.png")

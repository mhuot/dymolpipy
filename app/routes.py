from app import app
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def printit(mytext):
    xdimension = 970
    ydimension = 331
    img = Image.new('1', (xdimension,xdimension), 255) # 148?

    # fontsize = 100 # Three Lines
    # fontsize = 300 # One Line
    # fontsize = 150 # Two lines?
    fontsizes = [ 300, 150, 100 ]

    fontfile = '/System/Library/Fonts/Supplemental/Tahoma.ttf'
    # fontfile = '/usr/share/fonts/truetype/tahoma.ttf'
    width = 0
    printable = ""
    # labelContent = fill("12345678901234567890123456789012345678901234567890", 17)
    labelContent = "123456"
    # labelContent = "First second third fouth fifth Sixth Seventh eighth nineth tenth eleventh"
    # labelContent = "First second third fouth fifth Sixth Seventh eighth nineth tenth"
    # labelContent = "First second third"
    # labelContent = "Test second"
    # labelContent = "Test"
    labelWords = labelContent.split()

    for size in fontsizes:
        print(f"Checking size {size}")
        font = ImageFont.truetype(fontfile, size)
        lines = []
        fits = False
        linenumber = 0
        for word in labelWords:
            # print(f"Checking on word {word}")
            if lines: 
                # print(f"Let's test adding {word} to existing line {linenumber} that has '{lines[linenumber]}'")
                currentline = lines[linenumber] + " " + word
            else: 
                # print(f"Cool! First word on this label will be {word}")
                currentline = word
            currentdim = font.getsize(currentline)[0]
            # print(f"After adding {word}, the current line dimension would be {currentdim} the max is {xdimension}")
            if  currentdim < xdimension:
                # print(f"We had room at line {linenumber} for {word}")
                fits = True
                if lines:
                    # print(f"Cool, we already have lines!")
                    # print(f"Updating line {linenumber} from '{lines[linenumber]}' to '{currentline}'")
                    lines[linenumber] = currentline
                else:
                    # print(f"No lines yet, let's add {currentline}")
                    lines.append(currentline)
            else:
                # print(f"Adding {word} to {currentline} exceeded the max.")
                if size == 100 and linenumber < 2:
                    # print(f"Line {linenumber} - {lines[linenumber]}")
                    linenumber += 1
                    lines.append(word)
                    # print(f"Line {linenumber} - {lines[linenumber]}")
                    currentline = word
                    # print(f"Start line {linenumber} for size {size} current line is now '{currentline}'")
                    fits = True
                elif size == 150 and linenumber < 1:
                    # print(f"Line {linenumber} - {lines[linenumber]}")
                    linenumber += 1
                    lines.append(word)
                    # print(f"Line {linenumber} - {lines[linenumber]}")
                    currentline = word
                    # print(f"Start line {linenumber} for size {size} current line is now '{currentline}'")
                    fits = True
                else:
                    fits = False
        if fits:
            print(f"We have a perfect fit at {size}")
            break

    if len(lines) > 1:
        mytext = "\n".join(lines)
    else:
        mytext = lines[0]

    d = ImageDraw.Draw(img)
    d.text((0,0), mytext, font=font)
    rotated = img.rotate(270)
    rotated = rotated.crop( (xdimension-ydimension, 0, xdimension, xdimension) )

    rotated.save('./output/rotated.png')
    img.save('./output/image.png', fillcolor="white")
    os.system(f"lpr -o ppi=300 ./output/rotated.png")

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/print/<string:labelContent>', methods=['GET'])
def printLabel(labelContent):
    printit(labelContent)
    return f"Printing a label that says {labelContent}"

@app.route('/reprint/<string:labelContent>/<int:number>', methods=['GET'])
def reprintLabel(labelContent,number):
    return f"Printing label with the text '{labelContent}'' {number} times"

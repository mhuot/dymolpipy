from PIL import Image, ImageDraw, ImageFont
import os
import sys
import platform

def printit(labelContent):
    xdimension = 970
    ydimension = 331
    img = Image.new('1', (xdimension,xdimension), 255)

    fontsizes = [ 300, 150, 100 ]

    platsystem = platform.system()
    if platsystem == 'Darwin':
        fontfile = '/System/Library/Fonts/Supplemental/Tahoma.ttf'
    elif platsystem == 'Linux':
        fontfile = '/usr/share/fonts/truetype/tahoma.ttf'
    elif platsystem == 'Windows':
        fontfile = 'tahoma' # I have not tested this
    else:
        print(f"I don't have a font setting for {fontfile}")
        fontfile = 'tahoma' # I have not tested this

    try:
        font = ImageFont.truetype(fontfile, fontsizes[0])
    except:
        print(f"Something went wrong, with setting the font")

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
    if(os.getenv('PRINT_LABEL', False)):
        try:
            os.system(f"lpr -o ppi=300 -P _192_168_1_201 ./output/rotated.png")
        except:
            print("Something is wrong with the printing setup")

def printtest():
    printit("First second third fouth fifth Sixth Seventh eighth nineth tenth eleventh")
    printit("First second third fouth fifth Sixth Seventh eighth nineth tenth")
    printit("First second third")
    printit("Test second")
    printit("Test")
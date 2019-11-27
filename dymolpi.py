from PIL import Image, ImageDraw, ImageFont
import os
import sys
import platform

def sendtoprinter(imagefile):
    if(os.getenv('PRINT_LABEL', False) or os.getenv('LABEL_PRINTER')):
        try:
            if os.getenv('LABEL_PRINTER'):
                os.system(f"lpr -o ppi=300 -P {os.getenv('LABEL_PRINTER')} {imagefile}")
            else: 
                os.system(f"lpr -o ppi=300 {imagefile}")
        except:
            print("Something is wrong with the printing setup")

def setfont(fontname='tahoma'):
    platsystem = platform.system()
    if platsystem == 'Darwin':
        fontfile = f"/System/Library/Fonts/Supplemental/{fontname.capitalize()}.ttf"
    elif platsystem == 'Linux':
        fontfile = f"/usr/share/fonts/truetype/{fontname.lower()}.ttf"
    elif platsystem == 'Windows':
        fontfile = 'tahoma' # I have not tested this
    else:
        print(f"I don't have a font setting for {fontfile}")
        fontfile = 'tahoma' # I have not tested this

    try:
        font = ImageFont.truetype(fontfile, 12)
    except:
        print(f"Something went wrong, with setting the font")
    return fontfile

def makeimage(labelContent):
    xdimension = 970
    ydimension = 331
    img = Image.new('1', (xdimension,xdimension), 255)

    fontsizes = [ 300, 150, 100, 75 ]

    labelWords = labelContent.split()
    fontfile = setfont("tahoma");

    for size in fontsizes:
        font = ImageFont.truetype(fontfile, size)
        lines = []
        fits = False
        linenumber = 0
        for word in labelWords:
            if lines: 
                currentline = lines[linenumber] + " " + word
            else: 
                currentline = word
            currentdim = font.getsize(currentline)[0]
            if  currentdim < xdimension:
                fits = True
                if lines:
                    lines[linenumber] = currentline
                else:
                    lines.append(currentline)
            else:
                if ((size == 100 and linenumber < 2 ) or 
                    (size == 150 and linenumber < 1) or 
                    (size == 75 and linenumber < 3)):
                    linenumber += 1
                    lines.append(word)
                    currentline = word
                    fits = True
                else:
                    fits = False
        if fits:
            if os.getenv('DEBUG_LABEL_PRINTER', False):
                print(f"We have a perfect fit at {size}")
            break

    if len(lines) > 1:
        mytext = "\n".join(lines)
    else:
        mytext = lines[0]
    return mytext

def createimage(font, labelContent):
    d = ImageDraw.Draw(img)
    d.text((0,0), mytext, font=font)
    rotated = img.rotate(270)
    rotated = rotated.crop( (xdimension-ydimension, 0, xdimension, xdimension) )
    rotated.save('./output/rotated.png')
    sendtoprint('./output/rotated.png')
    if os.getenv('DEBUG_LABEL_PRINTER', False):
        img.save('./output/image.png', fillcolor="white")

def printit(labelContent):
    makeimage(labelContent)
    sendtoprinter('./output/rotated.png')

def printtest():
    printit("First second third fouth fifth Sixth Seventh eighth nineth tenth eleventh twelth thirteenth fourteenth fifteenth")
    printit("First second third fouth fifth Sixth Seventh eighth nineth tenth eleventh")
    printit("First second third fouth fifth Sixth Seventh eighth nineth tenth")
    printit("First second third")
    printit("Test second")
    printit("Test")

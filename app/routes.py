from app import app
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def printit(mytext):
    output = "./output"
    length = 986
    width = 331
    fontsize = 300
    img = Image.new('1', (length,length), 255) # Length is 1051 so we make a square of it and then we can rotate into a rectangle that is 1051x331

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fontsize) # System font so easy to deal with

    d = ImageDraw.Draw(img)
    d.text((0,0), mytext, font=font)
    rotated = img.rotate(270)
    rotated = rotated.crop( (length-width, 0, length, length) ) # Getting to the 1051x331 rectangle

    rotated.save(f"{output}/rotated.png")
    os.system(f"lpr -o ppi=300 {output}/rotated.png")

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/print/<string:labelContent>', methods=['GET'])
def printLabel(labelContent):
#    printit(labelContent)
    return f"Printing a label that says {labelContent}"

@app.route('/reprint/<string:labelContent>/<int:number>', methods=['GET'])
def reprintLabel(labelContent,number):
    return f"Printing label with the text '{labelContent}'' {number} times"

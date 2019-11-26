from app import app
from dymolpi import printit

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

from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return "<h1>hola gatito</h1>"

@app.route('/gatito/<name>')
def gatito(name):
    return "<h1>this is a page for {}</h1>".format(name)

@app.route('/puppy_latin/<name>')
def puppylatin(name):
    pupname = ''
    if name[-1] == 'y':
        pupname = name[:-1] + 'iful' 
        return "<h1>{} your name in puppylatin is {}</h1>".format(name,pupname)
    else:
        pupname = name[:-1] + 'y'
        return "<h1>{} your name in puppylatin is {}</h1>".format(name,pupname)

if __name__ == '__main__':
    app.run()
    debug == True
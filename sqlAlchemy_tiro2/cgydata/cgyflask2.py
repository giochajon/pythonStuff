import community_queries
from flask import Flask
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)





@app.route('/')
def index():
    return "<h1>Calgary community info </h1><br><p>add /community for the array or the /community/NAME to retreive the data</p> "

@app.route('/community/')
def listcom():
    lacom = community_queries.get_community_list()
    #return "{}".format(lacom)
    return json.dumps(lacom)

@app.route('/community/<name>')
def getdata(name):
    lacom = community_queries.get_community_by_name(name)
    #return "{}".format(lacom)
    return json.dumps(lacom)

if __name__ == '__main__':
    app.run()
    #debug == True
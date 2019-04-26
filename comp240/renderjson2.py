import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/load_excel/', methods=['GET'])
def get_excel_sheet():
    print('Called file')
    excel = pd.read_excel('./static/invoice.xlsx')
    output = excel.to_json(orient='records')
    return output




if __name__ == '__main__':
    app.debug = True
    app.run()
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nadaquever'


def rea():
	# see https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html
	#pd.set_option("display.max_rows", 100)
	pd.set_option("display.max_rows", None)
	
	df = pd.read_excel (r'./static/invoice.xlsx') #(use "r" before the path string to address special character, such as '\'). Don't forget to put the file name at the end of the path + '.xlsx'
	
	return df

@app.route('/')
def index():
	data = rea()
	return render_template('home.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
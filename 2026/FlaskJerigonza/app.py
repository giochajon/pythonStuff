from flask import Flask, request, jsonify
from flask_cors import CORS
from jerigonza import jerigonza  # Import the logic from jerigonza.py

app = Flask(__name__)
CORS(app) # Allows your HTML page to talk to this API

@app.route('/jerigonza', methods=['POST'])
def jerigonza_api():
    # Ensure we got valid JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    user_input = data.get("text", "")
    
    # Extract the filler parameter, defaulting to 'f' if not provided by the frontend
    filler_input = data.get("filler", "f")
    
    # Validate the filler just in case the frontend sends bad data
    if filler_input not in ['f', 'p']:
        filler_input = 'f'

    # Process the text using the imported function
    result = jerigonza(user_input, filler=filler_input)
    
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
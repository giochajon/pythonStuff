from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows your HTML page to talk to this API

def jerigonza_logic(text):
    vowels = "aeiouáéíóúAEIOUÁÉÍÓÚ"
    words = text.split()
    processed_words = []

    for word in words:
        if not word: continue
        
        if word[-1].lower() in vowels:
            transformed = "".join([c + 'f' + c.lower() if c.lower() in vowels else c for c in word])
            processed_words.append(transformed)
        else:
            last_vowel_idx = max([i for i, char in enumerate(word) if char.lower() in vowels], default=-1)
            if last_vowel_idx != -1:
                ending_consonant = word[-1]
                transformed = word[:last_vowel_idx + 1] + ending_consonant + word[last_vowel_idx + 1:]
                processed_words.append(transformed)
            else:
                processed_words.append(word)

    return " ".join(processed_words)

@app.route('/jerigonza', methods=['POST'])
def jerigonza_api():
    data = request.json
    user_input = data.get("text", "")
    result = jerigonza_logic(user_input)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
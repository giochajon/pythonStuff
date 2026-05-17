const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 5000;

// Enable CORS to allow your HTML frontend to communicate with the API
app.use(cors());

// Enable parsing of JSON request bodies
app.use(express.json());

/**
 * Translates a given text into Jerigonza.
 * @param {string} text - The input string to translate.
 * @returns {string} - The translated Jerigonza text.
 */
function jerigonza(text) {
    if (!text || typeof text !== 'string') return '';
    
    // Define vowels (including accented ones)
    const vowels = "aeiouáéíóúAEIOUÁÉÍÓÚ";
    const words = text.trim().split(/\s+/);
    const processedWords = [];

    for (const word of words) {
        if (!word) continue;
            
        // Check if the word ends in a vowel
        const lastChar = word[word.length - 1];
        if (vowels.includes(lastChar.toLowerCase())) {
            // Rule 1: For each vowel, add 'f' and the same vowel after it
            let transformed = "";
            for (const char of word) {
                if (vowels.includes(char.toLowerCase())) {
                    transformed += char + 'f' + char.toLowerCase();
                } else {
                    transformed += char;
                }
            }
            processedWords.push(transformed);
            
        } else {
            // Rule 2: Exception for words ending in a consonant
            // Find the index of the last vowel in the word
            let lastVowelIdx = -1;
            for (let i = word.length - 1; i >= 0; i--) {
                if (vowels.includes(word[i].toLowerCase())) {
                    lastVowelIdx = i;
                    break;
                }
            }
            
            if (lastVowelIdx !== -1) {
                // Add the ending consonant immediately after the last vowel
                const endingConsonant = word[word.length - 1];
                const transformed = 
                    word.slice(0, lastVowelIdx + 1) + 
                    endingConsonant + 
                    word.slice(lastVowelIdx + 1);
                processedWords.push(transformed);
            } else {
                // If there are no vowels (e.g., "sky"), keep the word as is
                processedWords.push(word);
            }
        }
    }

    return processedWords.join(" ");
}

// POST endpoint for translation matching the route in index.htm
app.post('/jerigonza', (req, res) => {
    const { text } = req.body;
    
    if (text === undefined || text === null) {
        return res.status(400).json({ error: "Missing 'text' field in request body." });
    }
    
    const result = jerigonza(text);
    return res.json({ result: result });
});

// Start the Express server
app.listen(PORT, () => {
    console.log(`Jerigonza API is running on http://127.0.0.1:${PORT}`);
});
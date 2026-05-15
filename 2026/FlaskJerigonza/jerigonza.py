
def jerigonza(text):
    # Define vowels (including accented ones for better language support)
    vowels = "aeiouáéíóúAEIOUÁÉÍÓÚ"
    words = text.split()
    processed_words = []

    for word in words:
        if not word:
            continue
            
        # Check if the word ends in a vowel
        if word[-1].lower() in vowels:
            # Rule 1: For each vowel, add 'f' and the same vowel after it
            transformed = ""
            for char in word:
                if char.lower() in vowels:
                    # We append the original char + 'f' + the lowercase version
                    transformed += char + 'f' + char.lower()
                else:
                    transformed += char
            processed_words.append(transformed)
            
        else:
            # Rule 2: Exception for words ending in a consonant
            # Find the index of the last vowel in the word
            last_vowel_idx = -1
            for i in range(len(word) - 1, -1, -1):
                if word[i].lower() in vowels:
                    last_vowel_idx = i
                    break
            
            if last_vowel_idx != -1:
                # Add the ending consonant immediately after the last vowel
                ending_consonant = word[-1]
                transformed = (
                    word[:last_vowel_idx + 1] + 
                    ending_consonant + 
                    word[last_vowel_idx + 1:]
                )
                processed_words.append(transformed)
            else:
                # If there are no vowels (e.g., "sky"), keep the word as is
                processed_words.append(word)

    return " ".join(processed_words)

print (jerigonza("esta es una prueba"))

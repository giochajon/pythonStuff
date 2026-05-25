import argparse
import sys

def jerigonza(text, filler='f'):
    """
    Transforms text into Spanish Jerigonza.
    """
    vowels = "aeiouáéíóúüAEIOUÁÉÍÓÚÜ"
    transformed = ""
    
    for char in text:
        if char in vowels:
            transformed += char + filler + char.lower()
        else:
            transformed += char
            
    return transformed

def main():
    # Set up the command line argument parser
    parser = argparse.ArgumentParser(description="Translate text to Spanish Jerigonza.")
    parser.add_argument("text", nargs="*", help="The text to translate")
    parser.add_argument("-f", "--filler", default="f", choices=['f', 'p'], 
                        help="The consonant to use as a filler ('f' or 'p')")
    
    args = parser.parse_args()
    
    # Join text arguments into a single string
    input_text = " ".join(args.text)
    
    # Allow reading from standard input (pipes) if no text argument is passed
    if not input_text:
        if not sys.stdin.isatty():
            input_text = sys.stdin.read().strip()
        else:
            parser.error("No text provided to translate.")
            
    # Print the result to the console
    print(jerigonza(input_text, filler=args.filler))

# This block only runs if the script is executed directly from the terminal
if __name__ == "__main__":
    main()
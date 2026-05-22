import speech_recognition as sr
import pyaudio
import wave
import io

def play_audio(audio_data):
    """Plays back the captured AudioData object directly from memory."""
    # Convert the audio data to a WAV format byte stream
    wav_bytes = audio_data.get_wav_data()
    wav_stream = io.BytesIO(wav_bytes)

    # Read the WAV stream
    wf = wave.open(wav_stream, 'rb')

    # Initialize PyAudio for playback
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Play the audio in chunks
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Cleanup playback
    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    # Initialize the recognizer
    r = sr.Recognizer()
    
    # Set the silence threshold to exactly 2.0 seconds
    # The recognizer will wait for 2 seconds of silence before finishing the recording
    r.pause_threshold = 2.0  

    with sr.Microphone() as source:
        print("Adjusting for background noise... please remain quiet.")
        # This listens for 2 seconds to establish the background noise floor
        r.adjust_for_ambient_noise(source, duration=2)
        print("\nListening...")
        print("(Say something containing the word 'repeat'. It will process after 2 seconds of silence)")

        while True:
            try:
                # Listen to the microphone
                audio = r.listen(source)

                # Recognize speech using Google's free Web Speech API
                text = r.recognize_google(audio).lower()
                print(f"Heard: \"{text}\"")

                # Check for the trigger word
                if "repeat" in text:
                    print("\nTrigger word 'repeat' detected!")
                    print("Playing back the audio...")
                    play_audio(audio)
                    print("Finished playing. Stopping program.")
                    break # Exits the loop and stops the program

            except sr.UnknownValueError:
                # This happens if it hears a noise but can't translate it to human speech
                print("[No recognizable speech detected, listening again...]")
            except sr.RequestError as e:
                # This happens if your internet connection fails
                print(f"Could not request results from Google Speech Recognition service; {e}")
                break

if __name__ == "__main__":
    main()
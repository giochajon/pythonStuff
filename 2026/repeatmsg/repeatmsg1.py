import speech_recognition as sr
import pyaudio
import wave
import io

def play_audio(audio_data):
    """Plays back the captured AudioData object directly from memory."""
    wav_bytes = audio_data.get_wav_data()
    wav_stream = io.BytesIO(wav_bytes)

    wf = wave.open(wav_stream, 'rb')
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Adjusting for background noise... please remain quiet.")
        r.adjust_for_ambient_noise(source, duration=2)
        
        # FIX 1: Turn off dynamic volume adjustment so the 2-second silence works properly
        r.dynamic_energy_threshold = False  

        print("\n--- PHASE 1 ---")
        print("Listening for the trigger word: 'repeat'...")
        
        # Set a short pause threshold just for catching the wake word quickly
        r.pause_threshold = 0.8 
        trigger_detected = False
        
        while not trigger_detected:
            try:
                wake_audio = r.listen(source)
                text = r.recognize_google(wake_audio).lower()
                
                if "repeat" in text:
                    trigger_detected = True
                    print("\n[Trigger 'repeat' detected!]")
            except sr.UnknownValueError:
                pass # Ignore background noises
            except sr.RequestError as e:
                print(f"Internet connection error: {e}")
                return

        print("\n--- PHASE 2 ---")
        print("Now recording your message...")
        print("(It will stop recording and play back after exactly 2 seconds of silence)")
        
        # FIX 2: Set the strict 2-second silence threshold for the actual recording
        r.pause_threshold = 2.0  
        
        try:
            # This captures the audio AFTER the trigger word was spoken
            message_audio = r.listen(source)
            
            print("\n2 seconds of silence detected! Playing back audio...")
            play_audio(message_audio)
            
            print("\nFinished playing. Stopping program.")
            
        except Exception as e:
            print(f"An error occurred during recording: {e}")

if __name__ == "__main__":
    main()
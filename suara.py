import speech_recognition as sr


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def get_speech(self):
        with sr.Microphone() as source:
            print("Say something...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Couldn't understand"
            except sr.RequestError:
                return "Error connecting to service"
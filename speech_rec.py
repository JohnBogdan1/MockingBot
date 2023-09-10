import os
import speech_recognition as sr
from gtts import gTTS
import pyaudio
import pyttsx3

engine = pyttsx3.init()
engine.say("I will speak this text")
engine.runAndWait()

voice = ""
myPyAudio = pyaudio.PyAudio()
print("Seeing pyaudio devices:", myPyAudio.get_device_count())

print(sr.Microphone.list_microphone_names())

mic = sr.Microphone()

print("Starting...")
while True:
    r = sr.Recognizer()
    with mic as source:
        try:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            text = r.recognize_google(audio)
            print(text)

            if text == "stop":
                break

            text = r.recognize_google(audio)
            voice += str(text)

            engine = pyttsx3.init()
            engine.say("I will speak this text")
            engine.runAndWait()
        except:
            print("say something...")

hr = gTTS(text=voice, lang="en", slow=False)
hr.save("1.wav")

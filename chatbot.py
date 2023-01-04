import adafruit_dotstar
import board
from digitalio import DigitalInOut, Direction, Pull
import gtts
import openai as ai
import os
import speech_recognition as sr
import sys

ai.api_key = os.getenv("OPENAI_API_KEY")

model_engine = "text-davinci-003"

mic = sr.Microphone(device_index=2)   
rec = sr.Recognizer()

def button_init():
    button = DigitalInOut(board.D17)
    button.direction = Direction.INPUT
    button.pull = Pull.UP
    return button

def LEDS_init():
    dots = adafruit_dotstar.DotStar(board.D6, board.D5, 3, brightness=0.2, auto_write=False)
    return dots

def speech_output(phrase):
    speech = gtts.gTTS(phrase, tld='ca')
    path = "response.mp3"
    speech.save(path)
    os.system("mpg123 -qf 6000 " + path)


def user_input():
    query = None
    try:
        with mic as source:
            print("listening...")
            for LED in range(3):
                LEDS[LED] = (255, 0, 0)
            LEDS.show()
            rec.adjust_for_ambient_noise(source, duration=0.5)
            query = rec.listen(source)
    
        return rec.recognize_google(query) 
    except sr.UnknownValueError:
        speech_output("I didn't catch that")
        sys.exit()

button = button_init()
LEDS = LEDS_init()

while True:
    if button.value:
        continue
    else:
        input_text = user_input()
        for LED in range(3):
            LEDS[LED] = (0, 0, 0)
        LEDS.show()
        completion = ai.Completion.create(
            engine=model_engine,
            prompt=input_text,
            max_tokens=1024,
            temperature=0.8,
            frequency_penalty=2.0,
        )   

        response = completion.choices[0].text

        print(response)
        speech_output(response)



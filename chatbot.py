import adafruit_dotstar
import board
from digitalio import DigitalInOut, Direction, Pull
import gtts
import openai as ai
import os
import speech_recognition as sr
import sys
import time
from threading import Thread

ai.api_key = os.getenv("OPENAI_API_KEY")

model_engine = "text-davinci-003"

mic = sr.Microphone(device_index=2)   
rec = sr.Recognizer()
LEDS = adafruit_dotstar.DotStar(board.D6, board.D5, 3, brightness=0.2, pixel_order='PRBG', auto_write=False)

def LEDS_reset():
    for LED in range(3):
        LEDS[LED] = (0, 0, 0)
    LEDS.show()

LEDS_reset()

def button_init():
    button = DigitalInOut(board.D17)
    button.direction = Direction.INPUT
    button.pull = Pull.UP
    return button

def LEDS_flash(compute_flag, stop):
    while compute_flag:
        for LED in range(3):
            LEDS[LED] = (255, 255, 255)
            LEDS.show()
            time.sleep(0.23)
            LEDS[LED] = (0, 0, 0)
            LEDS.show()
            time.sleep(0.001)
        if stop():
            break

def speech_output(phrase):
    speech = gtts.gTTS(phrase, tld='ca')
    path = "response.mp3"
    speech.save(path)
    os.system("mpg123 -qf 6000 " + path)
    return 0

def user_input(recognizer, audio):
    try:
        if rec.recognize_google(audio) == "computer":
            for LED in range(3):
                LEDS[LED] = (0, 255, 0)
            LEDS.show()
            print("listening...")
            try:
                query = rec.recognize_google(rec.listen(mic))
            except sr.UnknownValueError:
                speech_output("I didn't quite catch that")
                sys.exit()
            LEDS_reset()
            stop = False
            t_AI = Thread(target=compute_response, args=(query,))
            t_AI.start()
            t_LED = Thread(target=LEDS_flash, args=(t_AI.is_alive(), lambda: stop))
            t_LED.start()
            t_AI.join()
            stop = True
    except sr.UnknownValueError:
        pass

def compute_response(input_text):
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

def main():
    with mic as source:
        rec.adjust_for_ambient_noise(source)

    rec.listen_in_background(mic, user_input)
    while True:
        time.sleep(0.01)

if __name__ == '__main__':
    main()


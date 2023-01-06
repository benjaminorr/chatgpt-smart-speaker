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

OFF = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

ai.api_key = os.getenv("OPENAI_API_KEY")

mic = sr.Microphone(device_index=2)   
rec = sr.Recognizer()
LEDS = adafruit_dotstar.DotStar(board.D6, board.D5, 3, brightness=0.2, pixel_order='PRBG', auto_write=False)

def button_init():
    button = DigitalInOut(board.D17)
    button.direction = Direction.INPUT
    button.pull = Pull.UP
    return button

def LEDS_set(color):
    for LED in range(3):
        LEDS[LED] = color
    LEDS.show()

def LEDS_rotate(recognition_flag, stop):
    while recognition_flag:
        for LED in range(3):
            LEDS[LED] = WHITE
            LEDS.show()
            time.sleep(0.23)
            LEDS[LED] = OFF
            LEDS.show()
            time.sleep(0.001)
        if stop():
            break

def LEDS_flash(compute_flag, stop):
    while compute_flag:
        LEDS[0] = LEDS[2] = WHITE
        LEDS.show()
        time.sleep(0.4)
        LEDS[0] = LEDS[2] = OFF
        LEDS.show()
        time.sleep(0.001)
        LEDS[1] = WHITE
        LEDS.show()
        time.sleep(0.4)
        LEDS[1] = OFF
        LEDS.show()
        time.sleep(0.001)
        if stop():
            break

def speech_output(phrase):
    speech = gtts.gTTS(phrase, tld='ca')
    path = "response.mp3"
    speech.save(path)
    os.system("mpg123 -qf 6000 " + path)

def get_user_input():
        with mic as source:
            rec.adjust_for_ambient_noise(source, duration=0.5)
            print("listening...")
            LEDS_set(GREEN)
            query = rec.listen(source)    
            LEDS_set(OFF)
            return query

def recognize_input(audio, response):
    try:
        text = rec.recognize_google(audio)
    except sr.UnknownValueError:
        speech_output("I didn't catch that")
        sys.exit()
    compute_response(text, response)

def compute_response(input_text, response):
    completion = ai.Completion.create(
        engine="text-davinci-003",
        prompt=input_text,
        max_tokens=1024,
        temperature=0.8,
        frequency_penalty=2.0,
    )
    response[0] = completion.choices[0].text

def main():
    button = button_init()
    LEDS_set(OFF)

    while True:
        if button.value:
            continue
        else:
            input_audio = get_user_input()

            # threads: input/compute & LED rotate pattern
            response = [None]*1 
            stop_rotate = False
            t_rec = Thread(target=recognize_input, args=(input_audio, response,))
            t_rec.start()
            t_LED_rotate = Thread(target=LEDS_rotate, args=(t_rec.is_alive(), lambda: stop_rotate,))
            t_LED_rotate.start()
            t_rec.join()
            stop_rotate = True
          
            # threads: speak output & LED flash pattern
            stop_flash = False
            t_speak = Thread(target=speech_output, args=(response[0],))
            t_speak.start()
            t_LED_flash = Thread(target=LEDS_flash, args=(t_speak.is_alive(), lambda: stop_flash,))
            t_LED_flash.start()
            t_speak.join()
            stop_flash = True

if __name__ == '__main__':
    main()


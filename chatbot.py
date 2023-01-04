import gtts
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

model_engine = "text-davinci-003"

input_text = input("what you want\n")

completion = openai.Completion.create(
    engine=model_engine,
    prompt=input_text,
    max_tokens=1024,
    temperature=0.5,
    frequency_penalty=2.0,
)

response = completion.choices[0].text

print(response)

speech = gtts.gTTS(response, tld='com.au')
path = "response.mp3"
speech.save(path)
os.system("mpg123 -q " + path)

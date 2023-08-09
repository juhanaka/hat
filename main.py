import os
import speech_recognition as sr
from playsound import playsound
from tempfile import NamedTemporaryFile
from gtts import gTTS
from io import BytesIO

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

INTERMEDIATE_AUDIO_FILE = "/tmp/intermediate.mp3"


def get_completion(prompt, state=[]):
    new_state = state[:]
    if len(new_state) == 0:
        state.append({"role": "system", "content": "You are the Sorting Hat at Hogwarts from Harry Potter."})
    new_state.append({"role": "user", "content": prompt})
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=new_state)
    # Append the response to the state
    response_text = chat_completion.choices[0].message.content
    new_state.append({"role": "system", "content": response_text})
    return response_text, new_state


def prompt_for_input(text):
    user_input = input(text + "\n")
    return user_input


def get_output(user_input, state):
    output, state = get_completion(user_input, state)
    return output, state


def is_restart(user_input):
    return user_input == "restart"


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception: " + str(e))
    return said


def save_intermediate_audio():
    tts = gTTS("Hmmm.... Very well.", lang="en", tld="co.uk")
    tts.save(INTERMEDIATE_AUDIO_FILE)


def play_intermediate_audio():
    playsound(INTERMEDIATE_AUDIO_FILE, block=False)


def speak(text):
    gTTS(text=text, lang="en", tld="co.uk").write_to_fp(voice := NamedTemporaryFile())
    playsound(voice.name)
    voice.close()


def main():
    save_intermediate_audio()
    system_prompt = "You are the Sorting Hat at Hogwarts from Harry Potter."
    initial_text = "You are the Sorting Hat at Hogwarts from Harry Potter. You should ask me two questions one by one and sort me into a house. You should first introduce yourself and ask me my name."
    state = [{"role": "system", "content": system_prompt}]
    output, state = get_output(initial_text, state)
    while True:
        speak(output)
        user_input = get_audio()
        play_intermediate_audio()
        output, state = get_output(user_input, state)


main()

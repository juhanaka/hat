import os
import speech_recognition as sr
from playsound import playsound
from tempfile import NamedTemporaryFile
from gtts import gTTS
import threading

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

INTERSTITIAL_TEXTS = [
    "Intriguing. You may prove a challenge for me yet.",
    "Interesting. Let me think.",
    "I am starting to see the patterns forming.",
    "Curious. Very curious.",
]

SYSTEM_PROMPT = "You are the wise and ancient Sorting Hat at Hogwarts from the Harry Potter movies. Keep all your questions to a single sentence but your verdict can be longer and more thoughtful. You are conversational, and you speak naturally not in robotic, or verbose way."
INITIAL_TEXT = "You are the Sorting Hat at Hogwarts from Harry Potter. You should ask me three questions one by one and sort me into a house. Please keep everything to one sentence, and don't use the typical questions asked in such quizes, instead disguise the intent of the question with creative questions, riddles and introspective puzzles."


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


def save_interstitials():
    filenames = []
    for i, text in enumerate(INTERSTITIAL_TEXTS):
        tts = gTTS(text, lang="en", tld="co.uk")
        filename = f"/tmp/interstitial_{i}.mp3"
        tts.save(filename)
        filenames.append(filename)
    return filenames


def play_file(filename):
    playsound(filename)


def speak(text):
    gTTS(text=text, lang="en", tld="co.uk").write_to_fp(voice := NamedTemporaryFile())
    playsound(voice.name)
    voice.close()


def main():
    interstitials = save_interstitials()
    state = [{"role": "system", "content": SYSTEM_PROMPT}]
    output, state = get_output(INITIAL_TEXT, state)
    for i in range(100):
        speak(output)
        user_input = get_audio()
        interstitial = interstitials[i if i < len(interstitials) else len(interstitials) - 1]
        interstitial_thread = threading.Thread(target=play_file, args=(interstitial,))
        interstitial_thread.start()
        output, state = get_output(user_input, state)
        interstitial_thread.join()


main()

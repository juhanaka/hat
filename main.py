import os
import time

import openai
from whisper_mic.whisper_mic import WhisperMic
import torch
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


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


def main():
    mic = WhisperMic(
        model="small",
        english=False,
        device=("cuda" if torch.cuda.is_available() else "cpu"),
    )
    system_prompt = "You are the Sorting Hat at Hogwarts from Harry Potter."
    initial_text = "You are the Sorting Hat at Hogwarts from Harry Potter. You should ask me two questions one by one and sort me into a house. You should first introduce yourself and ask me my name."
    state = [{"role": "system", "content": system_prompt}]
    output, state = get_output(initial_text, state)
    while True:
        print("Sorting hat said: " + output)
        user_input = mic.listen()
        print("You said: " + user_input)
        output, state = get_output(user_input, state)


main()

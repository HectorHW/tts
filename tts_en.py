import io

import environs
import httpx
from pydub import AudioSegment
from pydub.playback import play

env = environs.Env()
env.read_env()

API_TOKEN: str = env("API_TOKEN")
API_URL: str = env("API_URL", "http://0.0.0.0:8000")

WavBytes = bytes


class ApiError(Exception):
    pass


def text_to_speach(value: str) -> WavBytes:
    response = httpx.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={"text": value},
    )
    if response.status_code != httpx.codes.OK:
        raise ApiError(response.text)
    return response.content


def say_given_text(value: str) -> None:
    wav = text_to_speach(value)
    segment = AudioSegment.from_wav(io.BytesIO(wav))
    play(segment)


input_buffer = ""

while True:
    try:
        command = input("tts> ").strip()
    except EOFError:
        break
    match command:
        case "quit" | "exit":
            break
        case "SAY":
            if not input_buffer:
                print("no text in buffer!")
                continue
            say_given_text(input_buffer)
            input_buffer = ""
        case _:
            input_buffer += " " + command

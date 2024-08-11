import silero
from pydub import AudioSegment
from pydub.playback import play
import pathlib

model, _ = silero.silero_tts(language="en", speaker="v3_en")

tmpdir = pathlib.Path.home() / ".tts"
tmpdir.mkdir(exist_ok=True)

output_file = tmpdir / "output.wav"


def say_given_text(value: str) -> None:
    ssml = f"""
    <speak>
    {value}
    <break time="100ms" />
    </speak>"""

    model.save_wav(ssml_text=ssml, speaker=f"en_51", audio_path=str(output_file))

    mysong = AudioSegment.from_wav(output_file)
    play(mysong)

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

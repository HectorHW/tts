import silero
import sys
from pydub import AudioSegment
from pydub.playback import play
import pathlib

text = " ".join(sys.argv[1:]).strip()

if not text:
    print("please provide non-empty text via arg", file=sys.stderr)
    sys.exit(1)

tmpdir = pathlib.Path.home() / ".tts"
tmpdir.mkdir(exist_ok=True)

model, _ = silero.silero_tts(language="en", speaker="v3_en")

output_file = tmpdir / "output.wav"

ssml = f"""
<speak>
{text}
<break time="100ms" />
</speak>"""

model.save_wav(ssml_text=ssml, speaker=f"en_51", audio_path=str(output_file))

mysong = AudioSegment.from_wav(output_file)
play(mysong)

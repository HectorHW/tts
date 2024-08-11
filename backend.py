import io
import secrets
import tempfile

import environs
import fastapi
import pydantic
import pydub
import silero
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

env = environs.Env()
env.read_env()

ALLOWED_TOKENS: list[str] = env.list("ALLOWED_TOKENS")

auth_scheme = HTTPBearer()


def verify_token(
    token: HTTPAuthorizationCredentials = fastapi.Depends(auth_scheme),  # noqa: B008
) -> None:
    for reference in ALLOWED_TOKENS:
        if secrets.compare_digest(token.credentials, reference):
            return
    raise fastapi.HTTPException(status_code=401, detail="invalid token")


app = fastapi.FastAPI()


class TTSPayload(pydantic.BaseModel):
    text: str


model, _ = silero.silero_tts(language="en", speaker="v3_en")


def say_given_text(value: str, output_path: str) -> None:
    ssml = f"""
    <speak>
    <break time="100ms" />
    {value}
    <break time="100ms" />
    </speak>"""

    model.save_wav(ssml_text=ssml, speaker="en_51", audio_path=output_path)


def convert_to_in_memory_mp3(segment: pydub.AudioSegment) -> bytes:
    buffer = io.BytesIO()
    segment.export(buffer, format="mp3")
    return buffer.getvalue()


@app.post(
    "/",
    responses={200: {"content": {"audio/mp3": {}}}},
    response_class=fastapi.Response,
    dependencies=[fastapi.Depends(verify_token)],
)
def text_to_speach(payload: TTSPayload) -> fastapi.Response:
    with tempfile.NamedTemporaryFile(suffix=".wav") as file:
        file.close()
        say_given_text(payload.text, file.name)
        mp3_data = convert_to_in_memory_mp3(pydub.AudioSegment.from_wav(file.name))
        return fastapi.Response(content=mp3_data, media_type="audio/mp3")

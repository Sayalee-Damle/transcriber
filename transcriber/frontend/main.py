import chainlit as cl
from chainlit.types import AskFileResponse
from pathlib import Path

from transcriber.configuration.log_factory import logger
from transcriber.configuration.config import cfg
import transcriber.backend.transcribe as transcribe


async def ask_user_msg(question) -> AskFileResponse:
    ans = None
    while ans == None:
        ans = await cl.AskUserMessage(
            content=f"{question}", timeout=cfg.ui_timeout
        ).send()
    return ans

def write_to_disc(file) -> Path:
    path = cfg.audio_file_path
    with open(path/"audio", "wb") as f:
        f.write(file.content)
    return path

@cl.on_chat_start
async def start() -> cl.Message:
    path_audio = await get_audio()
    file_transcribed =await transcribe.transcribe_from_vid(path_audio)
    if file_transcribed != "success":
        return "try again by restarting"
    


async def get_audio():
    files = None
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload an audio file to begin!",
            accept=[
                "audio/mpeg",
                "video/mp4",
	            "video/mpeg"
            ],
            max_files=1,
            max_size_mb = 100
        ).send()
    path_excel = write_to_disc(files[0])
    return path_excel
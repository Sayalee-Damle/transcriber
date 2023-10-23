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
    path = cfg.audio_file_path / "audio"
    with open(path, "wb") as f:
        f.write(file.content)
    return Path(path)


@cl.on_chat_start
async def start() -> cl.Message:
    path_audio = await get_audio()
    file_transcribed = await transcribe.get_transcribed_val(path_audio)
    #logger.info(file_transcribed)
    if file_transcribed == Exception:
        await cl.Message(content="try again by restarting").send()
        return
    else:
        while True:
            res = await cl.AskActionMessage(
                content="What do you want to do from the following?",
                actions=[
                    cl.Action(name="Download", value="Download", description="Download"),
                    cl.Action(name="Summarize", value="Summary", description="Summarize"),
                    cl.Action(name="Translate", value="Translate", description="Translate"),
                    cl.Action(name="Other", value="Other", description="Other"),
                    cl.Action(name="Exit", value="Exit", description="Exit"),
                ],
                timeout=cfg.ui_timeout
            ).send()
            action = res["value"]
            if action == "Download":
                await cl.Message(content="Download").send()
                await transcribe.save_text_to_file(file_transcribed)
                await cl.Message(
                    content="File downloaded sucessfully, check in the 'TranscribedText' folder created on your Computer"
                ).send()
            elif action in ("Summary"):
                await cl.Message(content="Summary", parent_id=res).send()
                await action_output(file_transcribed, action)
            elif action == "Translate":
                await cl.Message(content="Translate").send()
                lang = await ask_user_msg("Which language do you want to use?")
                output = await transcribe.translator(file_transcribed, lang)
                await cl.Message(content=f"{output}").send()
            elif action == "Exit":
                await cl.Message(content="Thank You!").send()
                break
            else:
                other_action = await ask_user_msg(
                    "What is the action that you want to perform on the transcribed text?"
                )
                await action_output(file_transcribed, other_action)


async def action_output(file_transcribed, action, language = "english"):
    output = await transcribe.document_tool(file_transcribed, action, language)
    await cl.Message(content=f"{output}").send()


async def get_audio():
    files = None
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload an audio file to begin!",
            accept=["audio/mpeg", "video/mp4", "video/mpeg"],
            max_files=1,
            max_size_mb=100,
        ).send()
    path_audio = write_to_disc(files[0])
    return path_audio

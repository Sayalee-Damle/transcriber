from asyncer import asyncify
import chainlit as cl
from chainlit.types import AskFileResponse
from pathlib import Path

from transcriber.configuration.log_factory import logger
from transcriber.configuration.config import cfg
import transcriber.backend.transcribe as transcribe
import transcriber.backend.tagging_service as ts
from transcriber.backend.model import ResponseTags


async def ask_user_msg(question):
    ans = None
    while ans == None:
        ans = await cl.AskUserMessage(
            content=f"{question}", timeout=cfg.ui_timeout, raise_on_timeout= True
        ).send()
    return ans


def write_to_disc(file) -> Path:
    path = cfg.audio_file_path / "audio"
    with open(path, "wb") as f:
        f.write(file.content)
    return Path(path)


@cl.on_chat_start
async def start() -> cl.Message:
    action_download = False
    action_summary = False

    path_audio = await get_audio()
    file_transcribed = await transcribe.get_transcribed_val(path_audio)
    # logger.info(file_transcribed)
    if file_transcribed == Exception:
        await cl.Message(content="try again by restarting").send()
        return
    else:
        await cl.Message(content=f"{file_transcribed}").send()
        while True:
            if action_summary == False and action_download == False:
                logger.info("in if")
                res = await summary_and_download()
                

            elif action_summary == True and action_download == False:
                logger.info("in elif 1")
                res = await download_nosummary()

            elif action_download == True and action_summary == False:
                logger.info("in elif 2")
                res = await nodownload_summary()

            else:
                logger.info("in else")
                res = await nosummary_nodownload()
            
            val = await value_res(res)
            logger.info("val: ")
            logger.info(val)
            if val == True:
                continue
            elif val == False:
                await cl.Message(content="Thank You!").send()
                break
            else:
                action = res["value"]
            if action == "Download":
                await cl.Message(content="Download Transcibed Text").send()
                action_download = True
                logger.info(action_download)
                response = await download_text(file_transcribed)
                await cl.Message(content=f"{response}").send()

            elif action == "Summary":
                action_summary = True
                logger.info(action_summary)
                await cl.Message(content="Summary").send()
                output = await action_output(file_transcribed, action)
                await cl.Message(content=f"{output}").send()
                download = await ask_user_msg(
                    "Do you want to download the text generated above?"
                )
                if answer(download) == "positive":
                    response = await download_text(output)
                    await cl.Message(content=f"{response}").send()

            elif action == "Translate":
                await cl.Message(content="Translate").send()
                lang = await ask_user_msg("Which language do you want to use?")
                output = await transcribe.translator(file_transcribed, lang)
                await cl.Message(content=f"{output}").send()
                download = await ask_user_msg("Do you want to download?")
                if answer(download) == "positive":
                    response = await download_text(output)
                    await cl.Message(content=f"{response}").send()

            elif action == "Exit":
                await cl.Message(content="Exit").send()
                await cl.Message(content="Thank You!").send()
                break
            else:
                await cl.Message(content="Other").send()
                other_action = await ask_user_msg(
                    "What is the action that you want to perform on the transcribed text?"
                )
                output = await action_output(file_transcribed, other_action)
                await cl.Message(content=f"{output}").send()
                download = await ask_user_msg("Do you want to download?")
                if answer(download) == "positive":
                    response = await download_text(output)
                    await cl.Message(content=f"{response}").send()

async def value_res(res):
    logger.info("in value res")
    
    logger.info(res)
    if res != None:
        logger.info("in value res - if")
        action = res["value"]
        return action
    else:
        logger.info("in value res - else")
        is_present = await chance()
        logger.info(is_present)
        return is_present
        
async def chance():
    logger.info('in chance')
    try:
        present = await ask_user_msg("Hi are you there?")
        logger.info(present)
        if present:
            if answer(present) == "positive":
                logger.info('in chance - if')
                return True
        else:
            logger.info('in chance - no answer')
      
    except:
        return False

async def nosummary_nodownload():
    return await cl.AskActionMessage(
                    content="What do you want to do from the following?",
                    actions=[
                        cl.Action(
                            name="Translate", value="Translate", description="Translate"
                        ),
                        cl.Action(name="Other", value="Other", description="Other"),
                        cl.Action(name="Exit", value="Exit", description="Exit"),
                    ],
                    timeout=cfg.ui_timeout,
                ).send()

async def nodownload_summary():
    return await cl.AskActionMessage(
                    content="What do you want to do from the following?",
                    actions=[
                        cl.Action(
                            name="Summarize", value="Summary", description="Summarize"
                        ),
                        cl.Action(
                            name="Translate", value="Translate", description="Translate"
                        ),
                        cl.Action(name="Other", value="Other", description="Other"),
                        cl.Action(name="Exit", value="Exit", description="Exit"),
                    ],
                    timeout=cfg.ui_timeout,
                ).send()

async def download_nosummary():
    return await cl.AskActionMessage(
                    content="What do you want to do from the following?",
                    actions=[
                        cl.Action(
                            name="Download", value="Download", description="Download"
                        ),
                        cl.Action(
                            name="Translate", value="Translate", description="Translate"
                        ),
                        cl.Action(name="Other", value="Other", description="Other"),
                        cl.Action(name="Exit", value="Exit", description="Exit"),
                    ],
                    timeout=cfg.ui_timeout,
                ).send()

async def summary_and_download():
    return await cl.AskActionMessage(
                    content="Do you want to do anything from the following?",
                    actions=[
                        cl.Action(
                            name="Download The Transcribed text",
                            value="Download",
                            description="Download",
                        ),
                        cl.Action(
                            name="Summarize", value="Summary", description="Summarize"
                        ),
                        cl.Action(
                            name="Translate", value="Translate", description="Translate"
                        ),
                        cl.Action(name="Other", value="Other", description="Other"),
                        cl.Action(name="Exit", value="Exit", description="Exit"),
                    ],
                    timeout=cfg.ui_timeout,
                ).send()


async def download_text(file_transcribed):
    await transcribe.save_text_to_file(file_transcribed)
    return "File downloaded sucessfully, check in the 'TranscribedText' folder created on your Computer"


async def action_output(file_transcribed, action, language="english"):
    output = await transcribe.document_tool(file_transcribed, action, language)
    return output


async def get_audio():
    files = None
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload an audio/video file to begin! The file should be in mp3, mp4 or mpeg format",
            accept=["audio/mpeg", "video/mp4", "video/mpeg"],
            max_files=1,
            max_size_mb=100,
        ).send()
    path_audio = await asyncify(write_to_disc)(files[0])
    return path_audio


def answer(input_msg: str):
    response_tags: ResponseTags = ts.sentiment_chain_factory().run(
        ts.prepare_sentiment_input(input_msg)
    )
    logger.info(response_tags)
    if response_tags.is_positive:
        return "positive"
    elif response_tags.is_negative:
        return "negative"
    elif response_tags.sounds_confused:
        return "confused"
    else:
        return "did not understand"

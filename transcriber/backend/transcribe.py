import whisper
from pathlib import Path
import uuid
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from pathlib import Path
from langchain.schema.messages import HumanMessage
from asyncer import asyncify

from transcriber.configuration.log_factory import logger
from transcriber.configuration.config import cfg
from transcriber.configuration.toml_support import read_prompts_toml
import transcriber.configuration.templates as t
prompts = read_prompts_toml()

def transcribe_from_vid(path: Path) -> dict:
    logger.info("in transcribe")
    assert path.exists(), f"path {path} does not exist"

    model = whisper.load_model("base")
    result = model.transcribe(path.as_posix(), fp16=False)
    logger.info("in try")
    transcribed_text = result['text']
    return transcribed_text

async def get_transcribed_val(path: Path)-> dict:
    return await asyncify(transcribe_from_vid)(path)

async def save_text_to_file(text: dict):
    logger.info("in 2nd func")
    try:
        #text_better = get_better_output(transcribed_text)
        with open(cfg.transcribed_text/ f"{uuid.uuid4()}.txt", "w") as file:
            file.write(text)
            logger.info("successful")
            return "success"
    except Exception as e:
        logger.exception("error")
        return str(e)


def prompt_factory(system_template, human_template):
    system_message_prompt = SystemMessagePromptTemplate.from_template(template= system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(template= human_template)
    messages = [system_message_prompt, human_message_prompt] 
    chat_prompt = ChatPromptTemplate.from_messages(messages)
    return chat_prompt

def get_better_output(text):
    prompt = prompt_factory(t.system_message, t.human_message)
    chain = LLMChain(llm=cfg.llm, prompt=prompt, verbose=cfg.verbose_llm)
    return chain.run({"text": text})

async def document_tool(text, action, language = "english"):
    prompt = prompt_factory(t.system_message_action, t.human_message_action)
    chain = LLMChain(llm=cfg.llm, prompt=prompt, verbose=cfg.verbose_llm)
    return await chain.arun({"text": text, "action": action, "lang": language})

async def translator(text, lang):
    prompt = prompt_factory(t.system_message_translator, t.human_message_translator)
    chain = LLMChain(llm=cfg.llm, prompt=prompt, verbose=cfg.verbose_llm)
    return await chain.arun({"text": text, "lang": lang})

if __name__ == "__main__":
    path_aud = Path(f"./recordings/ytmp3free.cc_how-i-learned-python-in-30-days-best-python-course-youtubemp3free.org.mp3")
    res = transcribe_from_vid(path_aud)
    logger.info(save_text_to_file(res))

import whisper
from pathlib import Path

from transcriber.configuration.log_factory import logger
from transcriber.configuration.config import cfg

model = whisper.load_model("base")

def transcribe_from_vid(path: Path) -> dict:
    result = model.transcribe(path)
    return result

def save_text_to_file(text: dict):
    try:
        transcribed_text = text['text']

        # Save the transcribed text to a file
        with open(cfg.transcribed_text, "w") as file:
            file.write(transcribed_text)
            logger.log("successful")
            return "success"
    except:
        logger.log("error")
        return "error"

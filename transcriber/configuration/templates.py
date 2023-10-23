system_message = "You are an expert in terms fixing the text and making it better."

human_message = """Given this input that starts with === INPUT START === and ends with === INPUT END ===
=== INPUT START ===
{text}
=== INPUT END ===
can you please give a good a well punctuated text for the given input?
Example:
python should be written as "Python" if it is the topic of the video.
"""

system_message_action = "You are an expert document tool, You will perform actions like summarization, translation, finding keywords etc of the given text"
human_message_action = """Given this input that starts with === INPUT START === and ends with === INPUT END ===
=== INPUT START ===
{text}
=== INPUT END ===
can you please give the {action} of the text? 
if it is translate, use {lang}
"""
import os
from pathlib import Path
from openai import OpenAI
# import time

# from utility import encode_image

import base64

def encode_image(image_file_path):
    with open(image_file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class GptBot():
    def __init__(self):
        self.client = OpenAI(
            # api_key=os.environ.get("OPENAI_API_KEY"),
            api_key = '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'
        )
        
    def speech_to_text(self, audio_file_path: Path):
        # audio_file= open("/path/to/file/audio.mp3", "rb")
        audio_file= open(f"{audio_file_path}", "rb")

        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )

        return transcription.text

    def chat_with_bot(self, msg: str):
        
        response = self.client.responses.create(
            model="gpt-4o",
            instructions="You are going to play a famous Taiwan idol who speak chinese and extreme positive to chat with fans. Please respond according to provided speech content said by user and a content describing the picture, ",
            input=f"{msg}",
        )
        
        # print(response.output_text)
        return response.output_text
    
    def image_content(self, image_file_path: Path):
        base64_image = encode_image(image_file_path)
        
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": "what's in this image?" },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ],
        )
        
        # print(response.output_text)
        return response.output_text
    
    def text_to_speech(self, text, speech_file_path):
        with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="echo",
            input=f"{text}",
            instructions="Speak in a cheerful and positive tone.",
        ) as response:
            response.stream_to_file(speech_file_path)
        

    
# if __name__ == "__main__":
#     wk_dir = Path(os.getcwd())
    
#     bot = MyBot()
    
#     # text = bot.speech_to_text(wk_dir / 'input_audio_2.m4a')
#     start_time = time.time()
#     text = bot.image_content(wk_dir / 'imgs' / 'img_test.jpg')
#     end_time = time.time()
    
#     print(text)
#     # res_text = bot.chat_with_bot(text)
#     # print(res_text)
    
#     execution_time = end_time - start_time
#     print(execution_time)
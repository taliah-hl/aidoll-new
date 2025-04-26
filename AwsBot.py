import os
from pathlib import Path
import boto3
import json
# import time
# from utility import encode_image
import base64

from constants import BEDROCK_KNOWLEDGE_BASE_ID, BEDROCK_MODEL_ID, REGION
from awsBots.awsChatBot import AwsChatBot
from awsBots.awsImageToText import AwsImageToText

def encode_image(image_file_path):
    with open(image_file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



class AwsBot():
    def __init__(self):
       # Initialize AWS credentials as before
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
        print("aws access key: ", self.aws_access_key_id)
        print("aws secrete key:",  self.aws_secret_access_key)
        print("aws session token:", self.aws_session_token)
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise EnvironmentError("AWS credentials are not set in the environment variables.")
        
        self.bedrock_agent_client = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=REGION,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token
        )
        
        self.bedrock_runtime_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-west-2',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token
        )
        
        self.knowledge_base_id = BEDROCK_KNOWLEDGE_BASE_ID
        
        
        
    def speech_to_text(self, audio_file_path: Path):
        # audio_file= open("/path/to/file/audio.mp3", "rb")
        audio_file= open(f"{audio_file_path}", "rb")

        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )

        return transcription.text

    def chat_with_bot(self, msg: str, image_description: str, use_knowledge_base:bool=False):
        aws_chat_bot =AwsChatBot(self.aws_access_key_id,self.aws_secret_access_key,self.aws_session_token)
        return aws_chat_bot.chat_with_bot(msg,image_description, use_knowledge_base)

    
    
    def image_content(self, image_file_path: Path=None):
        awsImageToText = AwsImageToText(self.aws_access_key_id, self.aws_secret_access_key, self.aws_session_token)
        return awsImageToText.detect_image_labels(image_file_path)

    
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
import os
from pathlib import Path
import boto3
import json
import requests
import wget
# import time
# from utility import encode_image
import base64

from openai import OpenAI

from constants import BEDROCK_KNOWLEDGE_BASE_ID, BEDROCK_MODEL_ID, REGION
from system_prompt import SYSTEM_PROMPT
from awsBots.awsChatBot import AwsChatBot
from awsBots.awsImageToText import AwsImageToText

BASE_URL = "https://persona-sound.data.gamania.com/api/v1/public/voice"
TOKEN    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhd3NfaGFja2F0aG9uIiwiZXhwaXJlcyI6MTc0NTc0ODAwMH0.9qpg1xraE_d_Hua2brAmCfRlQSce6p2kdipgq8j1iqo"


def encode_image(image_file_path):
    with open(image_file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class AwsBot():
    def __init__(self):
        self.client = OpenAI(
            # api_key=os.environ.get("OPENAI_API_KEY"),
            api_key = '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'
        )
        
        
       # Initialize AWS credentials as before
        print("AWS_ACCESS_KEY_ID:", os.environ.get('AWS_ACCESS_KEY_ID'))
        print("AWS_SECRET_ACCESS_KEY:", os.environ.get('AWS_SECRET_ACCESS_KEY'))
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
        self.bedrock_agent_client = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=REGION,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN')
        )
        
        self.bedrock_runtime_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-west-2',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN')
        )
        
        self.knowledge_base_id = BEDROCK_KNOWLEDGE_BASE_ID
        self.model_id = BEDROCK_MODEL_ID
        self.max_tokens = 500
        self.system_prompt=SYSTEM_PROMPT
        self.knowledge_base_id = "GWKCXUG2CA"
        
        
    def speech_to_text(self, audio_file_path: Path):
        # audio_file= open("/path/to/file/audio.mp3", "rb")
        audio_file= open(f"{audio_file_path}", "rb")

        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )

        return transcription.text

    def chat_with_bot(self, msg: str, image_description: str, use_knowledge_base:bool=False):
        aws_chat_bot =AwsChatBot(self.aws_access_key_id,self.aws_secret_access_key,self.aws_session_token, self.knowledge_base_id)
        return aws_chat_bot.chat_with_bot(msg,image_description, use_knowledge_base)

    
    
    def image_content(self, image_file_path: Path=None):
        awsImageToText = AwsImageToText(self.aws_access_key_id, self.aws_secret_access_key, self.aws_session_token)
        return awsImageToText.detect_image_labels(image_file_path)

    
    def text_to_speech(self, text, speech_file_path):
            
        speech_file_path.unlink(missing_ok=True)
        
        
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        params = {
            "text": f"{text}",
            "model_id": 6,
            "speaker_name": "puyang",
            "speed_factor": 1.0,
            "mode": "file"
        }
        
        try:
            res = requests.get(BASE_URL, headers=headers, params=params)
            res = res.json()
        except Exception as ex:
            print(f"{ex}")
            return
        
        wget.download(res['media_url'], out=str(speech_file_path))
        

    
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
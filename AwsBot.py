import os
from pathlib import Path
import boto3
import requests
import wget
import time
import base64

from openai import OpenAI

from constants import BEDROCK_KNOWLEDGE_BASE_ID, BEDROCK_MODEL_ID, REGION
from awsBots.awsChatBot       import AwsChatBot
from awsBots.awsImageToText    import AwsImageToText
from awsBots.AudioTranscriber import AudioTranscriber

BASE_URL = "https://persona-sound.data.gamania.com/api/v1/public/voice"
TOKEN    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhd3NfaGFja2F0aG9uIiwiZXhwaXJlcyI6MTc0NTc0ODAwMH0.9qpg1xraE_d_Hua2brAmCfRlQSce6p2kdipgq8j1iqo"

class AwsBot():
    def __init__(self):
        self.client = OpenAI(
            # api_key=os.environ.get("OPENAI_API_KEY"),
            api_key = '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'
        )
        
        
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
        
        self.chat_bot      = AwsChatBot(self.aws_access_key_id,self.aws_secret_access_key,self.aws_session_token)
        self.transcriber   = AudioTranscriber(bucket_name='conversationtestbucket')
        self.img_retriever = AwsImageToText(self.aws_access_key_id, self.aws_secret_access_key, self.aws_session_token)
        
        
        
    def speech_to_text(self, audio_file_path: Path):
        s3_key = 'audio/input_audio.wav' # file path on s3
        self.transcriber.upload_audio(str(audio_file_path), s3_key)
        
        job_name = f"audio_to_text_job_{int(time.time())}"
        self.transcriber.safe_start_transcription(job_name=job_name, media_format='wav', language_code='zh-TW')

        if self.transcriber.wait_for_completion() == 'COMPLETED':
            text = self.transcriber.get_transcribed_text()
            # return {"status": 200, 'text': f"{text}"}
            return text
        else:
            return "error"

    def chat_with_bot(self, msg: str, image_description: str, use_knowledge_base:bool=False):
        return self.chat_bot.chat_with_bot(msg,image_description, use_knowledge_base)

    
    def image_content(self, image_file_path: Path=None):
        return self.img_retriever.detect_image_labels(image_file_path)

    
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
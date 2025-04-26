import os
from pathlib import Path
import boto3
import json
# import time
# from utility import encode_image
import base64

from constants import BEDROCK_KNOWLEDGE_BASE_ID, BEDROCK_MODEL_ID, REGION
from system_prompt import SYSTEM_PROMPT

def encode_image(image_file_path):
    with open(image_file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



class AwsBot():
    def __init__(self):
       # Initialize AWS credentials as before
        print("AWS_ACCESS_KEY_ID:", os.environ.get('AWS_ACCESS_KEY_ID'))
        print("AWS_SECRET_ACCESS_KEY:", os.environ.get('AWS_SECRET_ACCESS_KEY'))

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
        
        
    def speech_to_text(self, audio_file_path: Path):
        # audio_file= open("/path/to/file/audio.mp3", "rb")
        audio_file= open(f"{audio_file_path}", "rb")

        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )

        return transcription.text

    def chat_with_bot(self, msg: str, use_knowledge_base:bool=False):
        response = None
        if not use_knowledge_base:
            response = self._chat_without_knowledge_base(msg)
        else:
            response = self._chat_with_knowledge_base(msg)

        if response['statusCode'] == 200:
                return response['body']['response']
        else:
            return "Generation Failed"
        return response
    
    def _chat_without_knowledge_base(self, msg:str):
        try:


            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": msg}]}
                ]
            })

            
            response = self.bedrock_runtime_client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            reply_text = response_body['content'][0]['text']
            
            return {
                'statusCode': 200,
                'body': {
                    'response': reply_text,
                    'mode': 'direct'
                }
            }
        except Exception as e:
            print(f"Error in direct model generation: {str(e)}")
            raise

    def _chat_with_knowledge_base(msg:str):
        pass
    
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
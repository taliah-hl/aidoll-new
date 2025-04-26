import os
from pathlib import Path
import boto3
import json
# import time
# from utility import encode_image
import base64

from constants import BEDROCK_KNOWLEDGE_BASE_ID, BEDROCK_MODEL_ID, REGION
from system_prompt import *


class AwsChatBot():
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, 
                 aws_session_token=None, region_name='us-west-2',knowledge_base_id=None):
       # Initialize AWS credentials as before
        print("AWS_ACCESS_KEY_ID:", os.environ.get('AWS_ACCESS_KEY_ID'))
        print("AWS_SECRET_ACCESS_KEY:", os.environ.get('AWS_SECRET_ACCESS_KEY'))

        self.bedrock_agent_client = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        
        self.bedrock_runtime_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        
        self.max_tokens = 500

        self.model_id = BEDROCK_MODEL_ID
        self.knowledge_base_id = knowledge_base_id

    def chat_with_bot(self, msg: str, image_description:str, use_knowledge_base:bool=False):
        response = None
        if not use_knowledge_base:
            response = self._chat_without_knowledge_base(msg, image_description)
        else:
            response = self._chat_with_knowledge_base(msg, image_description)

        if response['statusCode'] == 200:
                return response['body']['response']
        else:
            return "Generation Failed"

    def _chat_without_knowledge_base(self, msg:str, image_description:str, references:str=None):
        try:

            personality_prompt= PERSONALITY_PROMPT

            systen_prompt=PERSONALITY_PROMPT
            if references:
                systen_prompt+=f"參考對話範例：{references}"

            prompt = "這是用戶分享給你的照片內容:"
            prompt+=image_description
            prompt+="\n"
            prompt+="這是用戶的prompt:"
            prompt+=msg
            prompt = None
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ]
            })
            print("final prompt:", prompt)

            
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
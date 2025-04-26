import os
from pathlib import Path
import boto3
import json
# import time
# from utility import encode_image
import base64

from system_prompt import *


class AwsChatBot():
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, 
                 aws_session_token=None, region_name='us-west-2'):
       # Initialize AWS credentials as before


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
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.knowledge_base_id = "GWKCXUG2CA"

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

            system_prompt=PERSONALITY_PROMPT
            if references:
                system_prompt+=f"參考對話範例：{references}"
            system_prompt+=f"請根據這些對話的語氣與風格，回應粉絲的訊息：「{msg}」，並參考粉絲分享給你的照片內容"
            system_prompt+=REMINDER

            user_prompt = "這是粉絲分享給你的照片內容:"
            user_prompt+=image_description
            user_prompt+="\n"
            user_prompt+="這是粉絲的訊息:"
            user_prompt+=msg
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": user_prompt}]}
                ]
            })
            print("final prompt:", user_prompt)

            
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
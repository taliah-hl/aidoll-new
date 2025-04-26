import os
from pathlib import Path
import boto3
import json
# import time
# from utility import encode_image
import base64

from system_prompt import *

# CHAT_RECORD_PATH  = "chat_record.txt"

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

    def chat_with_bot(self, msg: str, image_description:str=None, file_path: str = ''):
        response = None
        response = self._send_request_to_bot(msg, image_description, references = "", file_path = file_path)

        if response['statusCode'] == 200:
            # chat_record_path = CHAT_RECORD_PATH

            #  save chat record
            try:
                with open(file_path, "a") as chat_file:
                    chat_file.write("User Prompt:\n")
                    chat_file.write(f"{msg}\n")
                    chat_file.write("Bot Response:\n")
                    chat_file.write(f"{response['body']['response']}\n")
                    chat_file.write("-" * 50 + "\n")  # Separator for readability
            except Exception as err:
                print("Error: cannot write to file:", err)
            return response['body']['response']
        else:
            return "不好意思，我聽不清楚，可以跟我再說一次嗎?"

    def _send_request_to_bot(self, msg:str, image_description:str=None, references:str=None, file_path: str = ""):
        try:
            system_prompt=PERSONALITY_PROMPT

            chat_history = ""
            chat_record_path = file_path
            if os.path.exists(chat_record_path):
                with open(chat_record_path, "r") as chat_file:
                    chat_history = chat_file.read()
            
            # Add chat history to the system prompt with a cue
            if chat_history:
                system_prompt += "以下是之前的聊天記錄，請參考這些記錄來回應粉絲的訊息：\n"
                system_prompt += chat_history
                system_prompt += "\n"

            #   chat references from knowledge base  
            if references:
                system_prompt+=f"參考對話範例：{references}"
            system_prompt+=f"請根據這些對話的語氣與風格，回應粉絲的訊息：「{msg}」，並參考粉絲分享給你的照片內容"
            system_prompt+=REMINDER

            # user prompt
            user_prompt=""
            # photo from user
            if image_description:
                user_prompt = "這是粉絲分享給你的照片內容:"
                user_prompt+=image_description
                user_prompt+="\n"

            # main prompt
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
            #print("final system prompt:", system_prompt)
            #print("final user prompt:", user_prompt)

            
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


    

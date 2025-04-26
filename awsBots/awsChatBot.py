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

    def image_to_response(self, msg: str, image_path:str=None, chat_record_path: str = ''):

        references = self._retrieve_references(msg)
         # Create Bedrock Runtime client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-west-2'  # specify your region
        )

        base64_image = self._encode_image_to_base64(image_path)

        user_prompt = PERSONALITY_PROMPT
        user_prompt += "請以偶像身分對這圖片作出回應。"
        user_prompt += "注意!請在尊重個人資料的情況下對人物進行描述。"

        chat_history = ""
        if os.path.exists(chat_record_path):
            try:
                with open(chat_record_path, "rb") as chat_file:  # Open in binary mode
                    chat_history = chat_file.read().decode('utf-8', errors='ignore')  # Decode as UTF-8, ignoring invalid bytes
            except Exception as e:
                print(f"Error reading chat record file: {e}")

        # Add chat history to the system prompt with a cue
        if chat_history:
            user_prompt += "以下是之前的聊天記錄，請參考這些記錄來回應粉絲的訊息：\n"
            user_prompt += chat_history
            user_prompt += "\n"

        # reference from knowledge base
        if references:
            user_prompt+=f"參考對話範例：{references}"
            user_prompt+=f"請根據這些對話的語氣與風格，回應粉絲的訊息：「{msg}」，並參考粉絲分享給你的照片內容"
            user_prompt+=REMINDER

        # main prompt
        user_prompt+="這是粉絲的訊息:"
        user_prompt+=msg

        print("final user prompt:", user_prompt)

        # Prepare the prompt
        whole_prompt = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
        }

        try:
            # Call the model
            response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # or your preferred Claude 3 model
                body=json.dumps(whole_prompt)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            description = response_body['content'][0]['text']
            
            return description

        except Exception as e:
            print(f"Error generating description: {str(e)}")
            return None
        
    def _encode_image_to_base64(self, image_path):
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def chat_with_bot(self, msg: str, image_description:str=None, file_path: str = ''):

        references = self._retrieve_references(msg)
        response = None
        response = self._send_request_to_bot(msg, image_description, references, file_path = file_path)

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


    def _retrieve_references(self, input_text, top_k=5):
        """從 Knowledge Base 檢索相關資料"""
        print("[AwsChatBot] Retrieve referece is running")
        try:
            response = self.bedrock_agent_client.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={"text": input_text},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": top_k
                    }
                }
            )
            references = [r["content"]["text"] for r in response["retrievalResults"]]
            return references
        except Exception as e:
            print(f"Error retrieving references: {str(e)}")
            # mock reference data
            return [
                "有養寵物嗎？其實我們家以前很愛養寵物耶。我們家養過好幾隻狗狗，然後都是很小的時候，所以他們年紀比較大就走了，然後也有養貓養兔子養蜥蜴，養蛇養天竺鼠養蜜賴五還養什麼我們家蠻愛養動物的，因為我媽很小，喜歡小動物養烏龜啊這些都有，所以我們家，但現在比較少了，現在比較現在只剩下一隻貓，然後兩隻狗一隻天竺鼠1個烏龜1個西一，",
                "我我老實講路的每一次，我好像都有小落淚，因為真的我跟你說現場看的那個感覺真的不一樣，如果你們有機會真的要現看現場看那個震撼啊。跟那種感動是很很難，很難像因為螢幕前面，其實有時候就是因為有剪接，有那個，你可以看到你的畫面，但是你不會被整個舞台的燈光效果跟所有人呈現的那個狀態去吸引，所以其實現場很容易感動，然後又看到大家這麼努力，然後知道不選愈加愈佳，我跟他合作過了啊。其實那時候愈佳，真的很厲害我跟你們以後知道愈佳，真的是厲害的，小孩什麼都會說實在的因為我自己認為我小時候很厲害但我覺得愈佳更厲害一家要不要上來跟我直播，但你要叫我怎麼咬人因為其實我好像不太會，",
                "浦洋是火星哭哭擔當沒有啦沒有喔我是火星，最愛哭，然後max是火星，最感性道是還有在其他新打網球，有我喜歡打網球，我蠻喜歡打網球，我喜歡打網球、排球羽球、桌球，我也喜歡，其實球類，我都還蠻喜歡的，我只有籃球，沒有那麼厲害，但是我我也喜歡我打，可能攔下，也長得比較高，跳得比較高，但我投得不是很準，但我會上來蠻愛上來，",
                "然後我看一下還有什麼呢？憑平常會煮飯嗎？其實會一點但沒有那麼會我們家因為我媽太會煮飯，了，我也我會煮飯，然後我們家也是開吃的，然後再是大附近溫州街泰順街，好像蠻多人知道叫糊塗麵，然後觀光也很常去吃，所以很可愛",
                "原子裡面的游泳，教練到底是誰呢？我覺得應該是我吧應該沒有人比我厲害喔"
            ]

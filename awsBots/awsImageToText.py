import boto3
import os
import json
import base64

from system_prompt import *

class AwsImageToText:

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name='us-west-2'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key  
        self.aws_session_token = aws_session_token
        self.region_name = region_name
 

    def detect_image_labels(self, model="aws", image_path=None):
        # Create a Rekognition client
        if not image_path:
            print("[image to text] No image provided.")
            return None
            #image_path = os.path.expanduser("~/data/test/mh/aidoll-new/imgs/people.jpg")

        if model == "aws":
            rekognition = boto3.client('rekognition',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,  # Specify your region
                aws_session_token=self.aws_session_token
            )
            
            # Read the image file
            with open(image_path, 'rb') as image:
                image_bytes = image.read()
            
            # Call Rekognition API
            response = rekognition.detect_labels(Image={'Bytes': image_bytes},
            MaxLabels=50,  # Maximum number of labels to return
            MinConfidence=70  # Minimum confidence score (0-100)
            )   
                # Extract detected labels

            detected_labels = []
            for label in response['Labels']:
                detected_labels.append({
                    'name': label['Name'],
                    'confidence': round(label['Confidence'], 2)
                })
            
            return json.dumps(detected_labels, indent=4)
            
        else:
            return self.get_image_descr_custom_model(image_path)
        

    
    def get_image_descr_custom_model(self, image_path):
         # Create Bedrock Runtime client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-west-2'  # specify your region
        )

        base64_image = self._encode_image_to_base64(image_path)

        user_prompt = PERSONALITY_PROMPT
        user_prompt += "請以偶像身分對這圖片作出回應。"
        user_prompt += "注意!請在尊重個人資料的情況下對人物進行描述。"


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


if "__main__" == __name__:
    imageToText = AwsImageToText( aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.environ.get('AWS_SESSION_TOKEN'))
    
    response = imageToText.detect_image_labels()
    print(response)
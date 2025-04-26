import boto3
import os
import json

class AwsImageToText:

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_session_token, region_name='us-west-2'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key  
        self.aws_session_token = aws_session_token
        self.region_name = region_name
 

    def detect_image_labels(self, image_path=None):
        # Create a Rekognition client
        if not image_path:
            print("Warning: no image provide, will use default image.")
            image_path = os.path.expanduser("~/data/test/mh/aidoll-new/imgs/people.jpg")
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
    
if "__main__" == __name__:
    imageToText = AwsImageToText( aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.environ.get('AWS_SESSION_TOKEN'))
    
    response = imageToText.detect_image_labels()
    print(response)
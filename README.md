# Aiodoll: Real-Time AI Idol Companion

Winning project of AWS Generative AI Hackathon 2025 (AI Idol Topic).

(Team Name: 風中凌亂, News coverage: https://www.bnext.com.tw/article/83255/awshackthon2025)

Aiodoll transforms a Raspberry Pi-powered doll into a smart, interactive AI companion! Enjoy real-time chats and image recognition, all infused with the personality and life story of your favorite idol!


## Features
- Real-time voice conversations mimicking your idolyour idol’s personality
- Remember your idol's life-history and talk like your idol
- Raspberry Pi-based hardware integration
- Mobile app connection for user interaction
   - Multimodal sensing: sees, listens, and responds

## Techniques
- Conversational AI with AWS Bedrock and Rekognition
- Retrieval Augmented Generation (RAG) using AWS Knowledge Base for personality mimicking
- Context awareness via conversational memory management


## Python testing script

Test this project's image response functionality by `python test_image_response.py`

## File Structure

```
│  .gitignore
│  AwsBot.py
│  main.py
│  README.md
│  test.py
│  tree.txt
│
├─awsServices
│      AudioTranscriber.py
│      awsChatBot.py
│      awsImageToText.py
│
├─config
│      system_prompt.py
│
├─piModules
│      Picam.py
│      Recorder.py
│
├─resources
│  └─can_audio
│          ActivitiesNotice.mp3
│          bye.mp3
│          Interlude.mp3
│          no_response_can_audio.mp3
│          opening_v1.mp3
│
├─test
│      test_image.jpg
│      test_image_to_response.py  <-- test file
│
└──tmp
   ├─repsonseSpeech
   ├─userPhoto
   └─userRecording
           input_audio.wav

```

## Technical Workflow

The Aiodoll system follows a structured workflow to process user interactions and generate responses:

1. **Audio to Text Conversion**

   - User audio input is captured and processed using **AWS Transcribe** to convert speech into text.

2. **Text to Knowledge Base Retrieval**

   - The transcribed text is used to query a **knowledge base** to retrieve relevant information.

3. **Text Processing and Response Generation**

   - The retrieved information, combined with a predefined system prompt, is sent to **AWS Bedrock Claude 3** to generate a response in the form of a sonnet.

4. **Response to Audio Conversion**
   - The generated response is converted back to audio using a **public voice API** and played back to the user.

### Workflow Diagram

```plaintext
User Audio Input
       ↓
AWS Transcribe (Audio → Text)
       ↓
Knowledge Base Query (Retrieve Relevant Info)
       ↓
AWS Bedrock Claude 3 (Generate Response)
       ↓
Public Voice API (Text → Audio)
       ↓
Audio Output to User
```

This workflow ensures seamless interaction between the user and the Aiodoll system, leveraging AWS services and APIs for efficient processing.

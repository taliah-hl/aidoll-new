# Aiodoll
Aiodoll is a Raspberry Pi-based interactive system that connects with a mobile app to engage with users in real time.
It includes a basic Python testing script to simulate and verify image response functionality.

## Features
Raspberry Pi-based hardware integration

Mobile app connection for user interaction

## Python testing script

`python test_image_response.py`


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
│      test_image_to_response.py
│
└──tmp
   ├─repsonseSpeech
   ├─userPhoto
   └─userRecording
           input_audio.wav

```

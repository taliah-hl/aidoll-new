import os
from pathlib import Path
import bluetooth
import pygame

from Recorder import Recorder
from Picam    import MyPicam
# from GptBot      import GptBot
from AwsBot import AwsBot

if __name__ == "__main__":
    # ------ dir, path setting ------ #
    wk_dir = Path(os.path.dirname(__file__))
    
    rec_dir = wk_dir / 'recordings'
    sph_dir = wk_dir / 'speechs'
    img_dir = wk_dir / 'imgs'
    
    rec_dir.mkdir(mode=777, parents=True, exist_ok=True)
    sph_dir.mkdir(mode=777, parents=True, exist_ok=True)
    img_dir.mkdir(mode=777, parents=True, exist_ok=True)
    
    # devices and services setting
    rec   = Recorder()
    bot   = AwsBot()
    picam = MyPicam()
    picam.start()
    
    # speaker initiate
    pygame.mixer.init()
    
    # ------ bluetooth setting ------ #
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    print(f"Listening on port {port}")

    # ------ Receive data ------ #
    while(True):
        client_sock, address = server_sock.accept()
        print(f"Accepted connection from {address}")

        try:
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                data = data.decode('utf-8')
                
                # print(f"Received: {data}")
                
                op = data
                if(op == "Start recording."):
                    rec.start()
                elif(op == "Stop recording."):
                    rec.stop()
                elif(op == "Take a picture."):
                    picam.capture(img_dir / 'img.jpg')
                elif(op == "Invoke response."):
                    prompt = {}
                    text = bot.speech_to_text(rec_dir / 'record.wav')
                    print(f"Speech content   : {text}")
                    prompt["Speech content"] = f"{text}"
                    
                    text = bot.image_content(img_dir/ 'img_test.jpg')
                    print(f"Image Content : {text}")
                    prompt["Image Content"] = f"{text}"
                    
                    print(str(prompt))
                    
                    res_text = bot.chat_with_bot(str(prompt))
                    print(f"Response : {res_text}")
                    print(res_text)
                    
                    bot.text_to_speech(res_text, sph_dir / 'response.mp3')
                    
                    pygame.mixer.music.load(str(sph_dir / 'response.mp3'))
                    pygame.mixer.music.play()

                    # Wait until the sound finishes
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    
                client_sock.send(data)  # echo back
        except OSError as ex:
            print(ex)
            client_sock.close()
            
    picam.close()
    

    # client_sock.close()
    server_sock.close()

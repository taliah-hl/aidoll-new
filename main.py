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
    can_dir = wk_dir / 'can_audio'
    
    rec_dir.mkdir(mode=777, parents=True, exist_ok=True)
    sph_dir.mkdir(mode=777, parents=True, exist_ok=True)
    img_dir.mkdir(mode=777, parents=True, exist_ok=True)
    can_dir.mkdir(mode=777, parents=True, exist_ok=True)
    
    # devices and services setting
    rec   = Recorder(out_dir=str(rec_dir))
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
        
        pygame.mixer.music.load(str(can_dir / 'opening_v1.mp3'))
        pygame.mixer.music.play()
        
        try:
            while True:
                data = client_sock.recv(1024)
                print(data)
                if not data:
                    break
                data = data.decode('utf-8')
                
                # print(f"Received: {data}")

                # Wait until the sound finishes
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                op = data
                if(op == "Cue me."):
                    rec.start()
                    picam.capture(img_dir / 'img.jpg')
                elif(op == "Cue ok."):
                    msg               = ''
                    image_description = ''
                    
                    rec.stop()
                    
                    msg = bot.speech_to_text(rec_dir / 'record.wav')
                    print(f"Speech content   : {msg}")
                    
                    image_path=img_dir/ 'img_test.jpg'
                    chat_record_path = wk_dir / 'chat_record.txt'
                    
                    res_text = bot.image_to_response(msg, image_path, chat_record_path)
                    print(f"Response : {res_text}")
                    print(res_text)
                    
                    bot.text_to_speech(res_text, sph_dir / 'response.mp3')
                   

                    pygame.mixer.music.load(str(sph_dir / 'response.mp3'))
                    pygame.mixer.music.play()
                    
                    # # Wait until the sound finishes
                    # while pygame.mixer.music.get_busy():
                    #     pygame.time.Clock().tick(10)
                    
                client_sock.send(data)  # echo back
        except OSError as ex:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            
            try:
                rec.stop()
            except:
                pass
                

            print(ex)
            client_sock.close()
            
    picam.close()
    

    # client_sock.close()
    server_sock.close()

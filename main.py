import os
from pathlib import Path
import bluetooth
import pygame

from piModules.Recorder import Recorder
from piModules.Picam    import MyPicam
from AwsBot import AwsBot

if __name__ == "__main__":
    # ------ dir, path setting ------ #
    wk_dir = Path(os.path.dirname(__file__))
    
    rec_dir = wk_dir / 'tmp/userRecording'
    sph_dir = wk_dir / 'tmp/responseSpeech'
    img_dir = wk_dir / 'tmp/userPhoto'
    can_dir = wk_dir / 'resources/can_audio'
    
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
                    
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    interlude = pygame.mixer.Sound(str(can_dir / 'Interlude.mp3'))
                    # pygame.mixer.music.load(str(can_dir / 'Interlude.mp3'))
                    interlude.set_volume(0.3)
                    interlude.play(loops=-1)
                    
                    msg = bot.speech_to_text(rec_dir / 'record.wav')
                    print(f"Speech content   : {msg}")
                    
                    
                    res_text = bot.image_to_response(msg, str(img_dir / 'img.jpg'), str(wk_dir / 'chat_record.txt'))
                    print(f"Response : {res_text}")
                    # print(res_text)
                    
                    bot.text_to_speech(res_text, sph_dir / 'response.mp3')
                    
                    interlude.stop()
                    pygame.mixer.music.load(str(sph_dir / 'response.mp3'))
                    pygame.mixer.music.play()
                    
                    # # Wait until the sound finishes
                    # while pygame.mixer.music.get_busy():
                    #     pygame.time.Clock().tick(10)
                elif(op == "Notification."):
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    pygame.mixer.music.load(str(can_dir / 'ActivitiesNotice.mp3'))
                    pygame.mixer.music.play(start=4.0)
                elif(op == "Mute."):
                    try:
                        interlude.stop()
                    except:
                        pass
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    
                # client_sock.send(data)  # echo back
        except Exception as ex:
            try:
                interlude.stop()
            except:
                pass
            try:
                pygame.mixer.music.stop()
            except:
                pass
            
            try:
                rec.stop()
            except:
                pass
            
            pygame.mixer.music.load(str(can_dir / 'bye.mp3'))
            pygame.mixer.music.play()
                

            print(ex)
            client_sock.close()
            
    picam.close()
    

    # client_sock.close()
    server_sock.close()

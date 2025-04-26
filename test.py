import os
# import timeouPicam
from playsound import playsound

# wk_dir = Path(os.getcwd())
if __name__ == "__main__":
    # output_dir = wk_dir / 'output'
    # output_dir.mkdir(parents=True, exist_ok=True)

    # picam = MyPicam()
    # picam.start()

    # picam.capture(wk_dir / 'output' / 'test.jpg')

    # picam.close()
    
    playsound("/home/pi/data/test/speechs/response.mp3")        # WAV/MP3/OGG supported
    
    
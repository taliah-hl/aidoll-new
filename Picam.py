import time
from picamera2 import Picamera2

class MyPicam(object):
    def __init__(self):
        self.cam: Picamera2 = Picamera2()

        preview_config = self.cam.create_preview_configuration()
        self.cam.configure(preview_config)

        # capture mode
        self.capture_config = self.cam.create_still_configuration()

    def start(self):
        self.cam.start() # wait until preview windows shows
        time.sleep(1)

    def capture(self, file_output):
        self.cam.switch_mode_and_capture_file(self.capture_config, file_output)
        print("Picture has been taken")

    def close(self):
        self.cam.close()
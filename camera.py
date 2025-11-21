import cv2, threading, vision

class RoboCamera:
    def __init__(self):
        self.is_killed = False
        self.frame_result = bytes()
        self.vision_callback = None
        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        except:
            self.cap = False
    def set_vision_callback(self, callback):
        self.vision_callback = callback
    def loop(self):
        print("start init")
        vision.initialize()
        vision.set_running()
        print("vis init")
        while not self.is_killed and self.cap:
            ret, frame = self.cap.read()
            if not ret: continue
            if self.vision_callback is not None:
                frame = vision.process_func(frame, self.vision_callback)
            
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90] #20=2.41sec, 4401bytes. 90=2.73, 19000bytes
            status, encimg = cv2.imencode('.jpg', frame, encode_param)
            self.frame_result = encimg.tobytes()
    def stop_thread(self):
        self.is_killed = True
    def get_b64(self):
        return self.frame_result

    def start_thread(self):
        self.t1 = threading.Thread(target = self.loop)
        self.t1.start()

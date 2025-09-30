import io

class FakeRelay():
    def __init__(self, pin=0):
        self.pin = pin
    def on(self):
        pass
    def off(self):
        pass
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False


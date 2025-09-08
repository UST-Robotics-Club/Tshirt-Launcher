import spark
import website
import robotcore
import threading
import os
import sys
from canmanager import is_raspberrypi
if __name__ == '__main__':
    if is_raspberrypi():
        os.chdir("/home/ustrobotics/Documents/")
    bot = robotcore.TShirtBot()
    def go():
        bot.main_loop()
    t = threading.Thread(target = go)
    t.start()
    try:
        website.run_site(bot)
    except KeyboardInterrupt:
        print("Stopping")
    bot.kill_thread()

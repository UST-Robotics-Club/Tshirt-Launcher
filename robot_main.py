import spark
import website
import robotcore
import threading
import os
if __name__ == '__main__':
    os.chdir("/home/ustrobotics/Documents/")
    bot = robotcore.TShirtBot()
    def go():
        bot.main_loop()
    t = threading.Thread(target = go)
    t.start()
    website.run_site(bot)

from spark import Spark
from canmanager import *

class TShirtBot:
    def __init__(self):
        self.can_manager = CanManager()
        self.spark_one = Spark(5)
        self.spark_two = Spark(6)
        self.can_manager.add_device(self.spark_one)
        self.can_manager.add_device(self.spark_two)

    def set_both(self, one, two):
        self.spark_one.set_percent(one)
        self.spark_two.set_percent(two)
        pass
    def set_one(self, power):
        self.spark_one.set_percent(power)
    def set_two(self, power):
        self.spark_two.set_percent(power)
    def tick(self):
        pass
    
    def main_loop(self):
        self.can_manager.start_thread()

        pass

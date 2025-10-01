from spark import SparkMax, StatusFrameID
from canmanager import *
import gpiozero
import time
import fakes
class TShirtBot:
    def __init__(self):
        self.can_manager = get_can_manager()
        self.front_left = SparkMax(15)
        self.back_left = SparkMax(12)
        self.front_right = SparkMax(11)
        self.back_right = SparkMax(10)
        #self.test_spark = SparkMax(16)
        self.enabled = False
        self.last_ping = 0
        self.is_killed = False
        self.turret = Turret()
        self.requested_left = 0
        self.requested_right = 0

    def kill_thread(self):
        self.can_manager.stop_bus()
        self.is_killed = True

    def refresh_ping(self):
        self.last_ping = time.time()

    def forward(self):
        self.front_left.set_duty_cycle(.1)
        self.front_right.set_duty_cycle(-.1)
        self.back_left.set_duty_cycle(.1)
        self.back_right.set_duty_cycle(-.1)

    def backward(self):
        self.front_left.set_duty_cycle(-.1)
        self.front_right.set_duty_cycle(.1)
        self.back_left.set_duty_cycle(-.1)
        self.back_right.set_duty_cycle(.1)

    def turn_left(self):
        self.front_left.set_duty_cycle(-.1)
        self.front_right.set_duty_cycle(-.1)
        self.back_left.set_duty_cycle(-.1)
        self.back_right.set_duty_cycle(-.1)

    def turn_right(self):
        self.front_left.set_duty_cycle(.1)
        self.front_right.set_duty_cycle(.1)
        self.back_left.set_duty_cycle(.1)
        self.back_right.set_duty_cycle(.1)

    def set_shooting(self, shooting):
        self.turret.set_shooting(shooting)

    def pulse_shoot(self, sec):
        self.turret.pulse_shoot(sec)

    def drive(self, forward: float, counterclockwise: float):
        right = forward - counterclockwise
        left = forward + counterclockwise
        if max(abs(right), abs(left)) > 1: # normalize if trying to go over 100%
            norm_factor = 1 / max(abs(right), abs(left))
            right *= norm_factor
            left *= norm_factor
        
        # print("r", right, ", l", left)
        self.requested_left = left
        self.requested_right = right

    def disable_drivetrain(self):
        self.front_left.set_duty_cycle(0)
        self.front_right.set_duty_cycle(0)
        self.back_left.set_duty_cycle(0)
        self.back_right.set_duty_cycle(0)

    def tilt_up(self):
        self.turret.tilter.set_duty_cycle(-0.1)

    def tilt_down(self):
        self.turret.tilter.set_duty_cycle(0.1)

    def rotate(self):
        self.turret.revolver_motor.set_duty_cycle(.1)

    def stop_turret(self):
        self.turret.revolver_motor.set_duty_cycle(0)
        self.turret.tilter.set_duty_cycle(0)

    def hold(self):
        self.turret.tilter.set_duty_cycle(.05)

    def set_enabled(self, enabled):
        print("Enabled: ", enabled)
        self.enabled = enabled
        self.can_manager.set_heartbeat(enabled)
        if not enabled:
            self.drive(0, 0)
            self.set_shooting(False)
        
    def get_enabled(self):
        return self.enabled
    
    def get_status_info(self):
        """Return whatever should be sent to the frontend every 0.75 sec"""
        return [self.get_enabled()]
    
    def tick(self):
        now = time.time()
        if now - self.last_ping > 1 and self.enabled:
            self.set_enabled(False)
        if self.enabled:
            self.front_left.set_duty_cycle(self.requested_left)
            self.back_left.set_duty_cycle(self.requested_left)

            self.front_right.set_duty_cycle(-self.requested_right)
            self.back_right.set_duty_cycle(-self.requested_right)
            self.turret.tick()
        else:
            self.drive(0, 0)
            
        time.sleep(0.02)
    
    def main_loop(self):
        self.can_manager.start_thread()
        while not self.is_killed:
            self.tick()

class Turret:
    def __init__(self):
        self.auto_shooting = False
        self.relay = gpiozero.LED(27) if fakes.is_raspberrypi() or 1 else fakes.FakeRelay()
        self.revolver_motor = SparkMax(6)
        self.tilter = SparkMax(5)
        self.time_end_shoot = 0
        self.last_shot_time = 0
        self.target_barrel_rotation = 0
        self.has_shot = False
        self.is_rotating = False
    
    def tick(self):
        # Sequence: RelayOn, wait time, RelayOff, Start revolver, wait until pos>=1 slot, stop revolver, repeat.

        now = time.time()
        during_shoot_period = now <= self.time_end_shoot
        in_shoot_cooldown = (now - self.last_shot_time) < 3
        #print(self.revolver_motor.get_encoder_position(), self.target_barrel_rotation)
        if during_shoot_period:
            #print("on+++++++")
            self.has_shot = True
            self.relay.on()
            self.last_shot_time = now
        else:
            #print("off------", self.auto_shooting, self.is_rotating)
            self.relay.off()
            if self.auto_shooting and not self.is_rotating and self.has_shot:
                self.has_shot = False
                self.is_rotating = True
                self.target_barrel_rotation = self.revolver_motor.get_encoder_position() + 20 # gear ratio is 5x4 = 20
        if self.target_barrel_rotation > self.revolver_motor.get_encoder_position():
            self.revolver_motor.set_duty_cycle(0.2)
        else:
            self.revolver_motor.set_duty_cycle(0)
            self.is_rotating = False
            if self.auto_shooting and not during_shoot_period and not in_shoot_cooldown:
                self.pulse_shoot(0.1)

    def disable(self):
        self.auto_shooting = False

    def set_shooting(self, shooting):
        self.auto_shooting = shooting

    def pulse_shoot(self, sec):
        self.time_end_shoot = time.time() + sec


from spark import SparkMax, StatusFrameID
from canmanager import *
import gpiozero
import time
import fakes
import camera
import cv2
import util
from vision import Landmark
class TShirtBot:
    def __init__(self):
        self.can_manager = get_can_manager()
        self.front_left = SparkMax(10)
        self.back_left = SparkMax(11)
        self.front_right = SparkMax(12)
        self.back_right = SparkMax(15)
        #self.test_spark = SparkMax(16)
        self.enabled = False
        self.last_ping = {}
        self.is_killed = False
        self.turret = Turret()
        self.requested_left = 0
        self.requested_right = 0
        self.camera = camera.RoboCamera()

    def kill_thread(self):
        self.is_killed = True

    def refresh_ping(self, sid):
        self.last_ping[sid] = time.time()

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
        self.turret.set_tilt_power(-0.1)

    def tilt_down(self):
        self.turret.set_tilt_power(0.05)

    def rotate(self):
        self.turret.revolver_motor.set_duty_cycle(.1)

    def stop_tilt(self):
        self.turret.hold()

    def rotate_left(self):
        self.turret.set_pivot_power(-0.075)

    def rotate_right(self):
        self.turret.set_pivot_power(0.075)
    
    def stop_pivot(self):
        self.turret.set_pivot_power(0)

    def manual_geneva(self, amount):
        self.turret.manual_geneva(amount)

    def hold(self):
        self.turret.tilter.set_duty_cycle(.05)
    def set_auto(self, auto):
        if auto == "none":
            self.camera.set_vision_callback(None)
            self.drive(0, 0)
        elif auto == "center":

            def callback(landmarks, frame):
                
                center = util.point_avg(landmarks[Landmark.LEFT_HIP], landmarks[Landmark.RIGHT_HIP])
                #print(center)
                cv2.circle(frame, [int(center.x * frame.shape[1]), int(center.y * frame.shape[0])], 5, [255,0,0])
                error = center.x*frame.shape[1] - frame.shape[1] / 2
                turn = util.abs_clamp(error * 0.009, -0.2, 0.2)
                print(error)
                self.drive(0, turn)

            self.camera.set_vision_callback(callback)
        pass
    def set_enabled(self, enabled):
        print("Enabled: ", enabled)
        if self.enabled == enabled: return
        self.enabled = enabled
        self.can_manager.set_heartbeat(enabled)
        if enabled:
            self.turret.enable()
        else:
            self.drive(0, 0)
            self.turret.disable()
            self.last_ping = {}
    def set_valve_time(self, time):
        self.turret.shoot_config["solenoid_time"] = time
    def get_valve_time(self):
        return self.turret.shoot_config["solenoid_time"]
    def get_enabled(self):
        return self.enabled
    
    def get_status_info(self):
        """Return whatever should be sent to the frontend every 0.1 sec"""
        return [self.get_enabled()]
    
    def tick(self):
        now = time.time()
        for ping in self.last_ping.values():
            if now - ping > 1 and self.enabled:
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

    def get_camera_frame(self):
        return self.camera.get_b64()
    
    def main_loop(self):
        self.can_manager.start_thread()
        self.camera.start_thread()
        while not self.is_killed:
            self.tick()
        self.turret.relay.close()
        self.can_manager.stop_bus()
        self.camera.stop_thread()
        

class Turret:
    def __init__(self):
        self.auto_shooting = False
        self.relay = OutputPin(27) if fakes.is_raspberrypi() else fakes.FakeRelay()
        self.revolver_motor = SparkMax(6) # thing running the geneva gear
        self.pivot_motor = SparkMax(21) # thing pivoting the turret
        self.tilter = SparkMax(5)
        self.time_end_shoot = 0
        self.last_shot_time = 0
        self.target_barrel_rotation = 0
        self.has_shot = False
        self.is_rotating = False
        self.target_tilt = 0
        self.manual_geneva_mode = False
        self.shoot_config = {
            "cooldown": 2, # 0 is for fast mode, 2 for normal mode
            "solenoid_time": 0.2, # seconds, 0.2 or 0.3 seems sufficient (doesn't significantly change shooting rate).
            "geneva_speed": 0.2 # 0.4 is for "fast mode", 0.2 for normal mode
        }
    
    def tick(self):
        # Sequence: RelayOn, wait time, RelayOff, Start revolver, wait until pos>=1 slot, stop revolver, repeat.

        now = time.time()
        during_shoot_period = now <= self.time_end_shoot
        in_shoot_cooldown = (now - self.last_shot_time) < self.shoot_config["cooldown"]
        #print(self.revolver_motor.get_encoder_position(), self.target_barrel_rotation)
        if during_shoot_period:
            #print("on+++++++")
            self.has_shot = True
            self.relay.on()
            self.last_shot_time = now
        else:
            #print("off------", self.auto_shooting, self.is_rotating)
            self.relay.off()
            if not self.is_rotating and self.has_shot:
                self.has_shot = False
                self.is_rotating = True
                if self.target_barrel_rotation == 0:
                    self.target_barrel_rotation = self.revolver_motor.get_encoder_position() + 20
                else:
                    self.target_barrel_rotation = self.target_barrel_rotation + 20
        if self.target_barrel_rotation > self.revolver_motor.get_encoder_position():
            if not self.manual_geneva_mode:
                self.revolver_motor.set_duty_cycle(self.shoot_config["geneva_speed"])
        else:
            if not self.manual_geneva_mode:
                self.revolver_motor.set_duty_cycle(0)
            self.is_rotating = False
            if self.auto_shooting and not during_shoot_period and not in_shoot_cooldown:
                self.pulse_shoot(self.shoot_config["solenoid_time"])
        if self.target_tilt != 0:
            #print(self.target_tilt, self.tilter.get_encoder_position())
            error = self.target_tilt - self.tilter.get_encoder_position()
            corr = max(min(error * 0.1, 0), -0.1)
            self.tilter.set_duty_cycle(corr)
            #print(corr)
        

    def disable(self):
        self.auto_shooting = False
        self.relay.off()
        self.target_tilt = 0
        self.tilter.set_duty_cycle(0)
        self.pivot_motor.set_duty_cycle(0)

    def enable(self):
        self.hold()

    def set_shooting(self, shooting):
        self.auto_shooting = shooting

    def pulse_shoot(self, sec):
        self.time_end_shoot = time.time() + sec

    def manual_geneva(self, amount):
        self.revolver_motor.set_duty_cycle(amount)
        self.manual_geneva_mode = amount != 0
        if amount == 0:
            self.target_barrel_rotation = self.revolver_motor.get_encoder_position()

    def set_tilt(self, angle):
        """Currently this doesn't work because there is no PID config on the tilter spark"""
        self.tilter.set_position(angle)

    def set_tilt_power(self, power):
        self.target_tilt = 0
        self.tilter.set_duty_cycle(power)

    def set_pivot_power(self, power):
        self.pivot_motor.set_duty_cycle(power)

    def hold(self):
        self.target_tilt = self.tilter.get_encoder_position()

class OutputPin:
    def __init__(self, pin):
        self.last_status = False
        self.pin = pin
    def set(self, on):
        if self.last_status != on:
            self.last_status = on
            os.system(f"sudo pinctrl set {self.pin} op d{'h' if on else 'l'}")
    def on(self):
        self.set(True)
    def off(self):
        self.set(False)
    def close(self):
        pass
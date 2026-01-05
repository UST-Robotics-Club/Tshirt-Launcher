import time
import robotcore
class UnstableController:
    """
    In normal mode, all control values received are continued at those values until a new one is received. 
    If more than 1000ms pass without a ping recieved, the connection is assumed lost and the robot fully disables.
    In a good connection, this leads to smoother driving and control. 

    Unstable mode assumes inputs or pings may be delayed significantly. It won't disable the robot in
    case of a late ping. Instead, it relies on periodic messages confirming a specific input like driving forward.
    When the connection is getting through successfully, these will be received every 100ms. If there is a delay of 
    150ms, the input will begin to slow down towards 0. By 250ms, it will have faded to 0. As soon as another message
    comes in, it will jump back to the commanded value. 
    In this way, even on a bad connection the robot will be able to move around, albeit jerkily. 
    """
    def __init__(self, robot: "robotcore.TShirtBot"):
        self.robot = robot
        self.drive_rotation = DecayingNumber() # lambda is handled by forward
        self.drive_forward = DecayingNumber(lambda val: robot.drive(val, self.drive_rotation.get()))
        self.turret_turn = DecayingNumber(lambda val: robot.turret.set_pivot_power(val))
        self.tilt = DecayingNumber(lambda val: robot.turret.set_tilt_power(val) if abs(val) > 0 else robot.stop_tilt())
        self.shoot = DecayingNumber(lambda val: robot.turret.set_shooting(val > 0))
        self.geneva = DecayingNumber(lambda val: robot.turret.manual_geneva(val))

    def set_shooting(self, shooting: bool, time):
        self.shoot.set(1.0 if shooting else 0.0, time)

    def set_drive(self, forward: float, rotation: float, time):
        self.drive_rotation.set(rotation, time)
        self.drive_forward.set(forward, time)

    def set_tilt(self, power: float, time):
        self.tilt.set(power, time)

    def set_turret_turn(self, power: float, time):
        self.turret_turn.set(power, time)

    def tick(self):
        for decaying in [self.drive_forward, self.drive_rotation, self.tilt, self.shoot, self.turret_turn]:
            decaying.tick()

    def reset(self):
        for decaying in [self.drive_forward, self.drive_rotation, self.tilt, self.shoot, self.turret_turn]:
            decaying.set(0.0, time.time())

class DecayingNumber:
    def __init__(self, immediateCallback = None):
        self.value = 0.0
        self.last_time = 0
        self.immediateCallback = immediateCallback
    def set(self, value: float, setTime: float):
        if setTime > self.last_time:
            if self.immediateCallback is not None:
                self.immediateCallback(value)
            self.value = value
            self.last_time = setTime
    def get(self) -> float:
        now = time.time()
        elapsed = (now - self.last_time) * 1000
        # trapezoidal decay. 0-150ms is full, 150-250 goes to zero.
        amount = self.value * (1 if elapsed < 150 else max(0, 1 - (elapsed - 150) / 100.0))
        return amount
    def tick(self):
        if self.immediateCallback is not None:
            self.immediateCallback(self.get())
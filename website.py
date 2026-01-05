import robotcore
import time
import socketio
from aiohttp import web

sio = socketio.AsyncServer(cors_allowed_origins='*')
robot: robotcore.TShirtBot
current_drivers = []

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    global current_drivers
    if sid in current_drivers and not robot.get_unstable_mode():
        robot.set_enabled(False)
        current_drivers = []
    print(f"Client disconnected: {sid}")

@sio.event
async def shoot(sid, sec):
    if sid not in current_drivers: return
    print("shoot!", sec)
    robot.pulse_shoot(sec)

@sio.event
async def autoshoot(sid, autoshoot, time):
    if sid not in current_drivers: return
    if robot.get_unstable_mode():
        robot.unstable_controller.set_shooting(autoshoot, time)
    else:
        robot.set_shooting(autoshoot)

@sio.event
async def drive(sid, forward, rotate, time):
    if sid not in current_drivers: return
    if robot.get_unstable_mode():
        robot.unstable_controller.set_drive(forward, rotate, time)
    else:
        robot.drive(forward, rotate)

@sio.event
async def stop(sid, time):
    if sid not in current_drivers: return
    print("Stop Driving!")
    robot.drive(0, 0)
    robot.unstable_controller.set_drive(0, 0, time.time())
    
@sio.event
async def tiltUp(sid, time):
    if sid not in current_drivers: return
    print("Tilting Up!")
    if robot.get_unstable_mode():
        robot.unstable_controller.set_tilt(-0.1, time)
    else:
        robot.tilt_up()
@sio.event
async def tiltDown(sid, time):
    if sid not in current_drivers: return
    print("Tilting Down!")
    if robot.get_unstable_mode():
        robot.unstable_controller.set_tilt(0.05, time)
    else:
        robot.tilt_down()
@sio.event
async def manualGeneva(sid, amount, time):
    if sid not in current_drivers: return
    if robot.get_unstable_mode():
        robot.unstable_controller.geneva.set(amount, time)
    else:
        robot.manual_geneva(amount)

@sio.event
async def stopTilt(sid, _):
    if sid not in current_drivers: return
    print("Turret Stopped")
    robot.stop_tilt()
    robot.unstable_controller.set_tilt(0, time.time())

@sio.event
async def hold(sid, time):
    if sid not in current_drivers: return
    print("Holding Turret")
    robot.hold()
    robot.unstable_controller.set_tilt(0, time.time())

@sio.event
async def turretLeft(sid, time):
    if sid not in current_drivers: return
    if robot.get_unstable_mode():
        robot.unstable_controller.set_turret_turn(-0.075, time)
    else:
        robot.rotate_left()

@sio.event
async def turretRight(sid, time):
    if sid not in current_drivers: return
    if robot.get_unstable_mode():
        robot.unstable_controller.set_turret_turn(0.075, time)
    else:
        robot.rotate_right()

@sio.event
async def stopPivot(sid, _):
    if sid not in current_drivers: return
    robot.stop_pivot()
    robot.unstable_controller.set_turret_turn(0, time.time())

@sio.event
async def setAuto(sid, auto):
    if sid not in current_drivers: return
    robot.set_auto(auto)

@sio.event
async def setValveTime(sid, time):
    if sid not in current_drivers: return
    robot.set_valve_time(time)
@sio.event
async def getValveTime(sid):
    return robot.get_valve_time()
@sio.event
async def setUnstableMode(sid, unstable):
    robot.set_unstable_mode(unstable)
@sio.event
async def frame(sid):
    return robot.get_camera_frame()

@sio.event
async def ping(sid):
    global current_drivers
    if sid in current_drivers:
        robot.refresh_ping(sid)
    if not robot.get_enabled():
        current_drivers = []
    return [current_drivers, robot.get_status_info()]

@sio.event
async def disable(sid):
    global current_drivers
    current_drivers = []
    robot.set_enabled(False)
    await sio.emit("disable")

@sio.event
async def enable(sid):
    global current_drivers
    current_drivers.append(sid)
    robot.refresh_ping(sid)
    robot.set_enabled(True)

@web.middleware
async def cache_control(request: web.Request, handler):
    response: web.Response = await handler(request)
    resource_name = request.match_info.route.name
    if resource_name and resource_name.startswith('static'):
        response.headers.setdefault('Cache-Control', 'no-cache')
    return response

async def index(request):
    with open('site/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

def run_site(bot: robotcore.TShirtBot):
    global robot
    robot = bot
    app = web.Application(middlewares=[cache_control])
    sio.attach(app)
    app.router.add_get('/', index)
    app.router.add_static('/', path="site/", name="static")
    try:
        web.run_app(app, port=5000)
    except:
        return

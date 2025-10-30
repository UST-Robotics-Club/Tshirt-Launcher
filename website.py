import robotcore

import socketio
from aiohttp import web

sio = socketio.AsyncServer(cors_allowed_origins='*')
robot: robotcore.TShirtBot
current_drivers = []

@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    global current_drivers
    if sid in current_drivers:
        robot.set_enabled(False)
        current_drivers = []
    """Handle client disconnection."""
    print(f"Client disconnected: {sid}")

@sio.event
async def shoot(sid, sec):
    if sid not in current_drivers: return
    print("shoot!", sec)
    robot.pulse_shoot(sec)

@sio.event
async def autoshoot(sid, autoshoot):
    if sid not in current_drivers: return
    robot.set_shooting(autoshoot)

@sio.event
async def drive(sid, forward, rotate):
    if sid not in current_drivers: return
    robot.drive(forward, rotate)

@sio.event
async def stop(sid):
    if sid not in current_drivers: return
    print("Stop Driving!")
    robot.drive(0, 0)
    
@sio.event
async def tiltUp(sid):
    if sid not in current_drivers: return
    print("Tilting Up!")
    robot.tilt_up()
@sio.event
async def tiltDown(sid):
    if sid not in current_drivers: return
    print("Tilting Down!")
    robot.tilt_down()
@sio.event
async def manualGeneva(sid, amount):
    if sid not in current_drivers: return
    robot.manual_geneva(amount)

@sio.event
async def rotateBarrels(sid):
    if sid not in current_drivers: return
    print("Barrels Be Rotating!")
    robot.rotate()
@sio.event
async def stopTilt(sid):
    if sid not in current_drivers: return
    print("Turret Stopped")
    robot.stop_turret()

@sio.event
async def hold(sid):
    if sid not in current_drivers: return
    print("Holding Turret")
    robot.hold()

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

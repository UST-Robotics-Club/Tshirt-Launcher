import robotcore

import socketio
from aiohttp import web

sio = socketio.AsyncServer(cors_allowed_origins='*')
robot: robotcore.TShirtBot
current_driver = ""

@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    global current_driver
    if sid == current_driver:
        robot.set_enabled(False)
        current_driver = ""
    """Handle client disconnection."""
    print(f"Client disconnected: {sid}")

@sio.event
async def shoot(sid, sec):
    if sid != current_driver: return
    print("shoot!", sec)
    robot.pulse_shoot(sec)
    #robot.set_two(float(req) / 100.0)


@sio.event
async def forward(sid):
    if sid != current_driver: return
    print("Drive Forward!")
    robot.forward()
@sio.event
async def backward(sid):
    if sid != current_driver: return
    print("Drive Backward!")
    robot.backward()
@sio.event
async def left(sid):
    if sid != current_driver: return
    print("Turn Left!")
    robot.turn_left()
@sio.event
async def right(sid):
    if sid != current_driver: return
    print("Turn Right!")
    robot.turn_right()
@sio.event
async def drive(sid, forward, rotate):
    if sid != current_driver: return
    robot.drive(forward, rotate)

@sio.event
async def stop(sid):
    if sid != current_driver: return
    print("Stop Driving!")
    robot.drive(0, 0)
    
@sio.event
async def tiltUp(sid):
    if sid!= current_driver: return
    print("Tilting Up!")
    robot.tilt_up()
@sio.event
async def tiltDown(sid):
    if sid!= current_driver: return
    print("Tilting Down!")
    robot.tilt_down()
@sio.event
async def rotateBarrels(sid):
    if sid != current_driver: return
    print("Barrels Be Rotating!")
    robot.rotate()
@sio.event
async def stopTurret(sid):
    if sid != current_driver: return
    print("Turret Stopped")
    robot.stop_turret()

@sio.event
async def hold(sid):
    if sid != current_driver: return
    print("Holding Turret")
    robot.hold()

    
@sio.event
async def ping(sid):
    global current_driver
    if sid == current_driver:
        robot.refresh_ping()
    if not robot.get_enabled():
        current_driver = ""
    return robot.get_enabled()

@sio.event
async def disable(sid):
    global current_driver
    current_driver = ""
    robot.set_enabled(False)
    await sio.emit("disable")

@sio.event
async def enable(sid):
    global current_driver
    if not current_driver:
        current_driver = sid
        robot.refresh_ping()
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

    web.run_app(app, port=5000)

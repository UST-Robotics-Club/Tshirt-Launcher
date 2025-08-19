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
async def spin1(sid, req):
    if sid != current_driver: return
    print("spin1!", req)
    robot.set_one(float(req) / 100.0)
    robot.set_two(float(req) / 100.0)

@sio.event
async def spin2(sid, req):
    if sid != current_driver: return
    print("spin2!", req)
    #robot.set_two(float(req) / 100.0)

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

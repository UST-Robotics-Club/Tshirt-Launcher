import robotcore

import socketio
from aiohttp import web
import os
import spark
import threading

sio = socketio.AsyncServer(cors_allowed_origins='*')
robot: robotcore.TShirtBot
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    print(f"Client disconnected: {sid}")

@sio.event
async def spin1(sid, req):
    print("spin!", req)
    robot.set_one(float(req) / 100)
@sio.event
async def spin2(sid, req):
    print("spin!", req)
    robot.set_two(float(req) / 100)
async def index(request):
    with open('site/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

def run_site(bot: "robotcore.TShirtBot"):
    global robot
    robot = bot
    app = web.Application()
    sio.attach(app)
    app.router.add_get('/', index)
    app.router.add_static('/', path="site/", name="static")

    web.run_app(app, port=5000)

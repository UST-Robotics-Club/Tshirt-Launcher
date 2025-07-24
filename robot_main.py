
import socketio
from aiohttp import web
import os
import spark
import threading

os.chdir("/home/ustrobotics/Documents/")
# Initialize the Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*') 
app = web.Application()
sio.attach(app)


@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    print(f"Client disconnected: {sid}")

async def index(request):
    with open('site/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')
@sio.event
async def spin(sid, req):
    print("spin!", req)
    spark.do_it(200000, float(req) / 100.0)
app.router.add_get('/', index)
app.router.add_get('/spin', spin)

app.router.add_static('/', path="site/", name="static")
t = threading.Thread(target = spark.main_loop)
if __name__ == '__main__':
    t.start()
    web.run_app(app, port=5000)

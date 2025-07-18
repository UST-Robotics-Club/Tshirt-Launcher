
import socketio
from aiohttp import web
import os
os.chdir("/home/ustrobotics/Documents/")
# Initialize the Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*') # Allow all origins for simplicity
app = web.Application()
sio.attach(app)

# Define Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    print(f"Client disconnected: {sid}")

@sio.event
async def my_message(sid, data):
    """Handle a custom 'my_message' event from the client."""
    print(f"Message from {sid}: {data}")
    # Acknowledge the message back to the client
    await sio.emit('server_response', {'status': 'received', 'message': data}, room=sid)

# Serve a basic HTML file for the client
async def index(request):
    with open('/site/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

def spin(req):
    pass
app.router.add_get('/', index)
app.router.add_get('/spin', index)

app.router.add_static('/site/', path="/", name="static")

if __name__ == '__main__':
    web.run_app(app, port=5000)

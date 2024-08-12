import asyncio
import websockets
import json
from collections import deque
import TobiiEyeTracker

WEBSOCKET_PORT = 8765
INTERVAL = 0.1  # Update interval in seconds

class WebSocketGazeTracker:
    def __init__(self):
        self.clients = set()
        self.gaze_queue = deque()
        self.last_location = None
        try:
            TobiiEyeTracker.init()
        except:
            pass
        print("Eye tracker initialized")

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"New client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")

    def get_movements(self):
        movements = list(self.gaze_queue)
        self.gaze_queue.clear()
        return movements

    def get_current_location(self):
        gaze_data = TobiiEyeTracker.getBuffer()
        if gaze_data:
            self.last_location = gaze_data[-1]  # Get the most recent point
            self.gaze_queue.extend(gaze_data)  # Append all new gaze data to the queue
        return self.last_location

    def checking_status(self):
        return len(self.gaze_queue) > 0

    async def update_gaze_data(self):
        while True:
            self.get_current_location()  # This now updates both last_location and gaze_queue
            await asyncio.sleep(INTERVAL)

    async def ws_handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                if data['command'] == 'get_movements':
                    movements = self.get_movements()
                    await websocket.send(json.dumps({'type': 'movements', 'data': movements}))
                elif data['command'] == 'get_current_location':
                    location = self.get_current_location()
                    await websocket.send(json.dumps({'type': 'current_location', 'data': location}))
                elif data['command'] == 'check_status':
                    status = self.checking_status()
                    await websocket.send(json.dumps({'type': 'status', 'data': status}))
        finally:
            await self.unregister(websocket)

    def run(self):
        server = websockets.serve(self.ws_handler, "localhost", WEBSOCKET_PORT)
        asyncio.get_event_loop().run_until_complete(server)
        print(f"WebSocket server started on ws://localhost:{WEBSOCKET_PORT}")
        asyncio.get_event_loop().create_task(self.update_gaze_data())
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    tracker = WebSocketGazeTracker()
    tracker.run()
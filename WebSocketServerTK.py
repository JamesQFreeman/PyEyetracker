import asyncio
import websockets
import json
import sys
import os
import time
from collections import deque
import tkinter as tk
from tkinter import ttk
import threading
import socket
import TobiiEyeTracker

class WebSocketGazeTracker:
    def __init__(self, port, interval, cache_size, log_callback):
        self.port = port
        self.interval = interval
        self.cache_size = cache_size
        self.clients = set()
        self.gaze_queue = deque(maxlen=cache_size)
        self.last_location = None
        self.server = None
        self.loop = None
        self.log_callback = log_callback

    async def register(self, websocket):
        self.clients.add(websocket)
        self.log_callback(f"New client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        self.log_callback(f"Client disconnected. Total clients: {len(self.clients)}")

    def get_movements(self):
        movements = list(self.gaze_queue)
        self.gaze_queue.clear()
        return movements

    def get_current_location(self):
        gaze_data = TobiiEyeTracker.getBuffer()
        self.log_callback(f"Reading: {len(gaze_data)} gaze points")
        gaze_data_time = [(x,y,int(time.time() * 1000)) for x,y in gaze_data]
        if gaze_data:
            self.last_location = (gaze_data[-1][0], gaze_data[-1][1])
            self.gaze_queue.extend(gaze_data_time)
        return self.last_location

    def checking_status(self):
        return len(self.gaze_queue) > 0

    async def update_gaze_data(self):
        while True:
            self.get_current_location()
            await asyncio.sleep(self.interval)

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

    async def start_server(self):
        self.server = await websockets.serve(self.ws_handler, "localhost", self.port)
        self.log_callback(f"WebSocket server started on ws://localhost:{self.port}")
        await self.server.wait_closed()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            TobiiEyeTracker.init()
        except:
            pass
        self.log_callback("Eye tracker initialized")
        self.loop.create_task(self.update_gaze_data())
        self.loop.run_until_complete(self.start_server())
        

    def stop(self):
        if self.server:
            self.server.close()
        if self.loop and self.loop.is_running():
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
            self.loop.stop()

class GazeTrackerGUI:
    def __init__(self, master):
        self.master = master
        master.title("WebSocket Gaze Tracker")
        
        self.tracker = None
        self.server_thread = None
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        ttk.Label(master, text="WebSocket Port:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.port_entry = ttk.Entry(master)
        self.port_entry.insert(0, "8765")
        self.port_entry.grid(row=0, column=1, padx=5, pady=5)

        
        
        ttk.Label(master, text="Update Interval (s):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.interval_entry = ttk.Entry(master)
        self.interval_entry.insert(0, "0.1")
        self.interval_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(master, text="Cache Size:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.cache_size_entry = ttk.Entry(master)
        self.cache_size_entry.insert(0, "10000")
        self.cache_size_entry.grid(row=2, column=1, padx=5, pady=5)

        self.start_button = ttk.Button(master, text="Start Server", command=self.start_server)
        self.start_button.grid(row=3, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(master, text="Stop Server", command=self.stop_server, state="disabled")
        self.stop_button.grid(row=3, column=1, padx=5, pady=5)

        self.status_label = ttk.Label(master, text="Server Status: Stopped")
        self.status_label.grid(row=4, column=0, padx=5, pady=5)

        self.test_port_button = ttk.Button(master, text="Test Port", command=self.test_port)
        self.test_port_button.grid(row=4, column=1, padx=5, pady=5)

        # Add text box for logs
        self.log_text = tk.Text(master, height=10, width=50)
        self.log_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)  # Make it read-only

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_server(self):
        port = int(self.port_entry.get())
        interval = float(self.interval_entry.get())
        cache_size = int(self.cache_size_entry.get())

        self.tracker = WebSocketGazeTracker(port, interval, cache_size, self.log_message)
        self.server_thread = threading.Thread(target=self.tracker.run)
        self.server_thread.start()

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Server Status: Running")
        self.log_message("Server started")

    def stop_server(self):
        if self.tracker:
            self.tracker.stop()
            self.log_message("Stopping server...")
            
            # Wait for the server to close gracefully
            timeout = 5  # 5 seconds timeout
            start_time = time.time()
            while self.server_thread.is_alive() and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # If the server is still running after timeout, force close it
            if self.server_thread.is_alive():
                os._exit(0)
            else:
                self.log_message("Server stopped successfully.")

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Server Status: Stopped")
        self.tracker = None
        self.server_thread = None

    def on_closing(self):
        if self.tracker:
            self.stop_server()
        self.master.destroy()

    def test_port(self):
        try:
            port = int(self.port_entry.get())
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                self.log_message(f"Port {port} is already in use.")
            else:
                self.log_message(f"Port {port} is available.")
            sock.close()
        except ValueError:
            self.log_message("Please enter a valid port number.")
        except Exception as e:
            self.log_message(f"An error occurred while testing the port: {str(e)}")

# compile to exe
# pyinstaller --onefile --windowed --icon=eye.ico --name=GazeServer WebSocketServerTK.py
if __name__ == "__main__":
    root = tk.Tk()
    gui = GazeTrackerGUI(root)
    root.mainloop()
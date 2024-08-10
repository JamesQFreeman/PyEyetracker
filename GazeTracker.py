import win32pipe, win32file, pywintypes
import struct
import time
import subprocess
import os

PIPE_NAME = r'\\.\pipe\TobiiGazeData'

# Define the structure of our gaze data
# Each gaze data point has a timestamp, x, and y coordinate
# 'f' for float (4 bytes)
GAZE_FORMAT = '!ff'  # timestamp, x, y
GAZE_SIZE = struct.calcsize(GAZE_FORMAT)
CACHE_SIZE = 65535
# PYTHON_32BIT = r""
PYTHON_32BIT = r"C:\Users\hz9423\anaconda3\envs\py32\python.exe"

class GazeTracker:
    '''
    This class is used to communicate with the Tobii Eye Tracker.
    It starts a subprocess () that reads the gaze data from the eye tracker
    and writes it to a named pipe. This class reads the data from the pipe.
    '''
    def __init__(self, python_32bit=PYTHON_32BIT):
        '''
        Initialize the GazeTracker class.
        '''
        if not python_32bit:
            raise Exception("Path to 32-bit Python executable not provided.")
        self.producer_process = None
        self.pipe = None
        python_32bit = PYTHON_32BIT
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the producer script
        producer_script = os.path.join(current_dir, "_listener_win32.py")
        self.producer_process = subprocess.Popen([python_32bit, producer_script])
        
        # Wait for the pipe to be created
        print("Waiting for the pipe to be created...")
        time.sleep(2)
        
        self.pipe = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )

    def get_movement(self):
        '''
        Get the gaze data from the pipe. 
        List of tuples (x, y), where x and y are floats [0,1].
        '''
        if not self.pipe:
            raise Exception("Pipe not initialized")
        
        try:
            # Read all available data from the pipe
            result, data = win32file.ReadFile(self.pipe, GAZE_SIZE * CACHE_SIZE)
            
            # Calculate how many complete gaze points we received
            num_points = len(data) // GAZE_SIZE
            
            # Unpack the data
            unpacked_data = struct.unpack(f'!{num_points * 2}f', data[:num_points * GAZE_SIZE])
            
            # Group into pairs (x, y)
            return list(zip(unpacked_data[::2], unpacked_data[1::2]))
        except pywintypes.error:
            # Handle pipe errors (e.g., broken pipe)
            print("Error in reading data from pipe")
            return []

    def cleanup(self):
        if self.pipe:
            win32file.CloseHandle(self.pipe)
        if self.producer_process:
            self.producer_process.terminate()
            self.producer_process.wait(timeout=5)
            if self.producer_process.poll() is None:
                self.producer_process.kill()

    def __del__(self):
        self.cleanup()
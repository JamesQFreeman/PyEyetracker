import win32pipe
import win32file
import pywintypes
import struct
import time
import TobiiEyeTracker

PIPE_NAME = r'\\.\pipe\TobiiGazeData'
GAZE_FORMAT = '!ff'  # timestamp, x, y
GAZE_SIZE = struct.calcsize(GAZE_FORMAT)
CACHE_SIZE = 65535
INTERVAL = 0.1

try:
    TobiiEyeTracker.init()
except:
    pass
print("Eye tracker initialized by listener_win32.py")

pipe = win32pipe.CreateNamedPipe(
    PIPE_NAME,
    win32pipe.PIPE_ACCESS_OUTBOUND,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
    1,
    GAZE_SIZE * CACHE_SIZE,
    GAZE_SIZE * CACHE_SIZE,
    0,
    None
)
print("Pipe created by listener_win32.py")


def run_listener():
    
    error_count = 0
    non_active_count = 0

    try:
        win32pipe.ConnectNamedPipe(pipe, None)
    except pywintypes.error:
        print("Error in establishing connection")
        return

    while True:
        try:
            gaze_data = TobiiEyeTracker.getBuffer()
            num_points = len(gaze_data)

            gaze_data = [p for tpl in gaze_data for p in tpl]
            packed_data = struct.pack(f'!{num_points * 2}f', *gaze_data)
            win32file.WriteFile(pipe, packed_data)
            time.sleep(INTERVAL)
            error_count = 0

            # Check if there are any active connections to the pipe
            pipe_info = win32pipe.PeekNamedPipe(pipe, 1024)
            if pipe_info is None or pipe_info[0] == 0:
                print("No active connections. Terminating listener.")
                non_active_count += 1
                if non_active_count > 6000: # 10 minutes
                    break

        except pywintypes.error:
            print("Error in writing data to pipe")
            error_count += 1
            if error_count > 10:
                break

run_listener()
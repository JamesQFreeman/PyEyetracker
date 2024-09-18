# PyEyetracker
A Python interface for the Tobii Eye Tracker. Supports GUI and websocket server.

![alt text](ReadmeImage/GUI.png)
## Features
- Support for both 32-bit and 64-bit (massive improvement, guys!) Python environments.
- Easy-to-use GazeTracker class for 64-bit applications compare to V1.
- Backward compatibility with the original 32-bit EyeTracker interface

## Usage Methods

### 1. WebSocket GUI

Download the executable from the releases page and run it. This provides a graphical interface and WebSocket server.

### 2. WebSocket Command Line

Run the WebSocket server from the command line:
   ```
   python WebSocketServer.py
   ```
### 3. Python Package

For 64-bit applications, use the new GazeTracker class:
   ```python
    from GazeTracker import GazeTracker
    import time

    # Start the eye tracker
    tracker = GazeTracker()

    for i in range(100):
        # Read data every second, result is a list of tuples (x, y)
        print(tracker.get_movement())
        time.sleep(1)
   ```
## Installation

### For Python Package:
1. Ensure you have Python installed (32-bit or 64-bit)
2. Install required dependencies:
   ```
   pip install pywin32 websockets
   ```
3. Copy `TobiiEyeTracker.pyd`, `tobii_stream_engine.dll`, `GazeTracker.py`, and `_listener_win32.py` into your project directory
4. Set up the `PYTHON_32BIT` path in `GazeTracker.py`

### For WebSocket Command Line 
1. install python 32bit (if you are using conda, try: `set CONDA_SUBDIR=win-32` and `conda create -n py32 python=3.7`)
2. install pywin32: `pip install pywin32 websockets`


## Development using c++
To develop additional functions, follow these steps:
1. Download Tobii Native Stream Engine using NuGet in Visual Studio
   - Open Package Manager Console
   - Search for "Tobii.StreamEngine" and install the package (This can no longer be done becase Tobii decided to sell its pro line for more money)
2. Follow the setup instructions in the [Visual Studio C++/Python integration guide](https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019)
3. Refer to the [Tobii Stream Engine API documentation](https://vr.tobii.com/sdk/develop/native/stream-engine/api/) for available functions and usage

## References
1. [Visual Studio C++/Python integration guide](https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019)
2. [Tobii Stream Engine API documentation](https://vr.tobii.com/sdk/develop/native/stream-engine/api/)

## License
See the [LICENSE](LICENSE) file for details.
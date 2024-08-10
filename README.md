# PyEyetracker
A Python interface for the Tobii Eye Tracker. Now V2!

## Features
- Support for both 32-bit and 64-bit (massive improvement, guys!) Python environments.
- Easy-to-use GazeTracker class for 64-bit applications compare to V1.
- Backward compatibility with the original 32-bit EyeTracker interface

## Usage
1. Download the .dll and .pyd files to your project's Python folder
2. For 64-bit applications, use the new GazeTracker class:
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

## Requirements and installation
1. A 32bit python and 64bit python which you can downloaded from [here](https://www.python.org/downloads/windows/).
2. Tobii Experience set up and running.
3. ```pip install pywin32``` for the 32bit python and the python env you gonna use. (see IPC design)
4. Copy ```TobiiEyeTracker.pyd, tobii_stream_engine.dll, GazeTracker.py, _listener_win32.py``` into you develop dir.
5. Setup ```PYTHON_32BIT = r"dir\to\your\python-32bit.exe"``` in ```GazeTracker.py```

## Inter-Process Communication (IPC) Design

PyEyetracker uses Windows named pipes for inter-process communication between the 32-bit data collection process and the 64-bit main application. Named pipes are chosen for several reasons:

1. Efficiency: They provide fast, low-overhead communication between processes on the same machine.
2. Simplicity: Named pipes are straightforward to implement and use in Python with the `win32pipe` and `win32file` modules.
3. Compatibility: They work seamlessly between 32-bit and 64-bit processes on Windows.
4. Reliability: Named pipes offer a robust, stream-oriented communication channel with built-in synchronization.

This IPC mechanism allows us to leverage the 32-bit Tobii SDK while still providing a 64-bit interface for modern Python environments, offering the best of both worlds in terms of compatibility and performance.

## Development using c++
To develop additional functions, follow these steps:
1. Download Tobii Native Stream Engine using NuGet in Visual Studio
   - Open Package Manager Console
   - Search for "Tobii.StreamEngine" and install the package
2. Follow the setup instructions in the [Visual Studio C++/Python integration guide](https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019)
3. Refer to the [Tobii Stream Engine API documentation](https://vr.tobii.com/sdk/develop/native/stream-engine/api/) for available functions and usage

## References
1. [Visual Studio C++/Python integration guide](https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019)
2. [Tobii Stream Engine API documentation](https://vr.tobii.com/sdk/develop/native/stream-engine/api/)

## License
See the [LICENSE](LICENSE) file for details.
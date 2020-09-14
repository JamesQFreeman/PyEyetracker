import TobiiEyeTracker

# Start the eye tracker
try:
    TobiiEyeTracker.init()
except:
    pass

# Read data every second
import time
for i in range(100):
    print(TobiiEyeTracker.getBuffer())
    time.sleep(1)
    
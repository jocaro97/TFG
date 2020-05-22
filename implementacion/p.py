import threading, time

def countTo(x=4,delay=0.1):
    for i in range(x):
        print(i)
        time.sleep(delay)

# Use keyword arguments on with the 4hz thread
thread4hz = threading.Thread(target=countTo,kwargs=dict(x=3,delay=0.25))
# Use the defualt arguments
thread10hz = threading.Thread(target=countTo)

thread4hz.start()
thread10hz.start()

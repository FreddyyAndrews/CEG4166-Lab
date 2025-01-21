import threading
import time

# Print hello function;
# variable n is seconds for sleep function, variable name is name used for wheels.
def helloWorld(n, name):
    print('Hello world {} '.format(name))
    time.sleep(n)

# Create a thread array, threads_list
threads_list = []

# Create new time variable, start, that captures time
start = time.time()

# Create first thread, t. Target is the function called in the thread, 
# name is the name of the thread, and args are the arguments for the function called.
# value 1 in args is seconds for the sleep function, and 'WheelRight' is sent
# to name variable in function helloWorld
t = threading.Thread(target=helloWorld, name='Thread Right', args=(1, 'WheelRight'))

# Append thread into thread array, threads_list
threads_list.append(t)

# Create thread t2 this time with 'WheelLeft' and append it into thread array
t2 = threading.Thread(target=helloWorld, name='Thread Left', args=(1, 'WheelLeft'))
threads_list.append(t2)

# Start both threads
t.start()
print('{} has started '.format(t.name))
t2.start()
print('{} has started '.format(t2.name))

# Loop within threads_list to join running threads before executing main thread
for i in threads_list:
    i.join()

# Create new time variable, end, that captures time
end = time.time()

print('time taken: {}'.format(end - start))
print('All 2 threads are done')

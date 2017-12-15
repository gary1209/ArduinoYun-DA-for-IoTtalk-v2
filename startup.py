import subprocess
import time

restart_period = 600

cycle = 0
timestamp = time.time()
while True:
    cycle = (cycle+1) % 10000
    print('Cycle', cycle)
    p = subprocess.Popen(['python', 'dai.py'])
    while time.time()-timestamp < restart_period:
        time.sleep(1)
    subprocess.Popen.kill(p)
    timestamp = time.time()
    print('Restarting...')
    print

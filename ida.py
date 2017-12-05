import random
from functools import partial
from uuid import getnode
import time
from dan import NoData
import custom
import sys
import os
import Queue
import threading

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient


idfInfo = custom.idf()
odfInfo = custom.odf()
ODFcache = {}
IDFcache = {}
odf2Bridge = {}
incomming = {}
for f_name in [t[0] for t in odfInfo]:
    incomming[f_name] = 0
timestamp = time.time()
    

os.system(r'echo "none" > /sys/class/leds/ds:green:usb/trigger')


class app(dict):
    global ODFcache, IDFcache, odf2Bridge

    host = custom.ServerIP
    device_name = custom.device_name
    device_model = custom.device_model
    #device_addr = "{:012X}".format(getnode())
    username = custom.username   # optional
    push_interval = custom.Comm_interval  # global interval

    idf_list = [t[0] for t in idfInfo]
    odf_list = []
    for t in odfInfo:
        if t[0] not in odf_list:
            odf_list.append(t[0])
            odf2Bridge[t[0]] = [[t[1], t[2]]]
        else:
            odf2Bridge[t[0]].append([t[1], t[2]])

    for ODF in odf_list:
        ODFcache[ODF] = Queue.Queue(maxsize=1)
    
    for IDF in idf_list:
        IDFcache[IDF] = Queue.Queue(maxsize=1)
    
    print('Detected idf:')
    for idf in idf_list:
        print('    {}'.format(idf))
    print('Detected odf:')
    for odf in odf_list:
        print('    {}'.format(odf))


    def __init__(self):	
        for DF in idfInfo:
            function_name = DF[0].replace('-','_')
            self.__dict__[function_name] = partial(self.forIDF, DF[0])

        for DF in self.odf_list:
            function_name = DF.replace('-','_')
            self.__dict__[function_name] = partial(self.forODF, DF)
            
    @staticmethod
    def forIDF(idf_name):
        global IDFcache
        if IDFcache[idf_name].qsize():
            os.system(r'echo "default-on" > /sys/class/leds/ds:green:wlan/trigger')
            value = IDFcache[idf_name].get()

            '''
            print 'IDF:({f}, {v!r})'.format(
                         f=idf_name, v=value,)
            '''
            
            os.system(r'echo "none" > /sys/class/leds/ds:green:wlan/trigger')
            return value
        else:
            return NoData()
            
    @staticmethod
    def forODF(odf_name, data):
        os.system(r'echo "default-on" > /sys/class/leds/ds:green:wlan/trigger')
        global ODFcache 

        if ODFcache[odf_name].qsize():
            ODFcache[odf_name].get()
            ODFcache[odf_name].put(data)
        else:    
            ODFcache[odf_name].put(data)
      
        os.system(r'echo "none" > /sys/class/leds/ds:green:wlan/trigger')
                

def Bridge2Arduino():
    global incomming, ODFcache, IDFcache, timestamp
    while True:
        for ODF in ODFcache:
            if ODFcache[ODF].qsize():	
                data = ODFcache[ODF].get()
            
                if data == None:
                    continue

                for dimension in odf2Bridge[ODF]:
                    if data[dimension[0]] is None:
                             continue

                    BridgeClient().put(dimension[1], str(int(data[dimension[0]])))

                    '''                                         
                    print '{f}[{d}] -> {p} = {v}, incomming[{f}] = {i}'.format(
                                f=ODF,
                                d=dimension[0],
                                p=dimension[1],
                                v=str(int(data[dimension[0]])),
                                i=incomming[ODF],)
                    '''            
                    
                    incomming[ODF] = incomming[ODF] ^ 1                                                                                                                                   
                    BridgeClient().put('incomming_'+ODF, str(incomming[ODF]))
            else:                                        
                #print(ODF, 'queue is empty.')
                pass

        if time.time() - timestamp >= app.push_interval: 
            for IDF in idfInfo:
                tmp = BridgeClient().get(IDF[0])
                if tmp is None:
                    pass
                else:
                    v = IDF[1](tmp)
                    if v is not None:
                        if IDFcache[IDF[0]].qsize():
                            IDFcache[IDF[0]].get()
                            IDFcache[IDF[0]].put(v)
                        else:
                            IDFcache[IDF[0]].put(v)
            timestamp = time.time()        

t = threading.Thread(target=Bridge2Arduino) 
t.daemon = True
t.start()


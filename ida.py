from functools import partial
from uuid import getnode
import time, sys, os, Queue
from dan import NoData
import custom

sys.path.insert(0, '/usr/lib/python2.7/bridge/')
from bridgeclient import BridgeClient

idfInfo = custom.idf()
odfInfo = custom.odf()
ODFcache = {}
IDFcache = {}
IDFsignal = {}
odf2Bridge = {}
incomming = {}
for f_name in [t[0] for t in odfInfo]:
    incomming[f_name] = 0
timestamp = time.time()


os.system(r'echo "none" > /sys/class/leds/ds:green:usb/trigger')
os.system(r'echo "none" > /sys/class/leds/ds:green:wlan/trigger')


class app(dict):
    global ODFcache, IDFcache, odf2Bridge

    api_url = custom.ServerIP
    device_name = custom.device_name
    device_model = custom.device_model
    device_addr = "{:012X}".format(getnode())
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

    def __init__(self):	
                                                                                                                                                
        for DF in idfInfo:
            function_name = DF[0].replace('-','_')
            self.__dict__[function_name] = partial(self.forIDF, DF[0])

        for DF in self.odf_list:
            function_name = DF.replace('-','_')
            self.__dict__[function_name] = partial(self.forODF, DF)

        for ODF in self.odf_list:
            ODFcache[ODF] = Queue.Queue(maxsize=1)
            
        for IDF in self.idf_list:
            IDFcache[IDF] = Queue.Queue(maxsize=1)

        print('Detected idf:')
        for idf in self.idf_list:
            print('    {}'.format(idf))
        print('Detected odf:')
        for odf in self.odf_list:
            print('    {}'.format(odf))
                                            
            
    @staticmethod
    def forIDF(idf_name):
        global IDFcache, IDFsignal
        IDFsignal[idf_name] = 1
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


BClient = BridgeClient()
def Bridge2Arduino():
    global incomming, ODFcache, IDFcache, timestamp, IDFsignal

    while True:  
        for ODF in ODFcache:
            if ODFcache[ODF].qsize():	
                data = ODFcache[ODF].get()
            
                if data == None:
                    continue

                for dimension in odf2Bridge[ODF]:
                    if data[dimension[0]] is None:
                             continue
                    
                    BClient.put(dimension[1], str(int(data[dimension[0]])))

                    '''                                         
                    print '{f}[{d}] -> {p} = {v}, incomming[{f}] = {i}'.format(
                                f=ODF,
                                d=dimension[0],
                                p=dimension[1],
                                v=str(int(data[dimension[0]])),
                                i=incomming[ODF],)
                    '''            

                    incomming[ODF] = incomming[ODF] ^ 1       
                    BClient.put('incomming_'+ODF, str(incomming[ODF]))
            else:
                pass

        if time.time() - timestamp >= app.push_interval: 
            for IDF in idfInfo:
                if IDFsignal.get(IDF[0]):
                    tmp = BClient.get(IDF[0])
                    IDFsignal[IDF[0]] = 0
                else:
                    tmp = None    

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




